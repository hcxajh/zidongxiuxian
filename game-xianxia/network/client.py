"""
修仙游戏 - WebSocket 客户端实现
用于连接游戏服务器并进行实时通信
"""

import asyncio
import json
import logging
from typing import Optional, Callable, Dict, Any
from network import (
    MessageType, GameMessage, PlayerState, Room, 
    NetworkSyncBase, SyncManager, create_sync_message
)


logger = logging.getLogger(__name__)


class GameClient(NetworkSyncBase):
    """游戏客户端 - 连接服务器并同步游戏状态"""
    
    def __init__(self, server_url: str = "ws://localhost:8765"):
        super().__init__()
        self.server_url = server_url
        self.websocket = None
        self.player_id: Optional[str] = None
        self.player_name: Optional[str] = None
        self.current_room: Optional[Room] = None
        self.sync_manager = SyncManager()
        self._receive_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._connected = False
        self._reconnect_delay = 5.0
        self._max_reconnect_attempts = 5
        self._reconnect_count = 0
        
        # 回调函数
        self.on_connect: Optional[Callable] = None
        self.on_disconnect: Optional[Callable] = None
        self.on_error: Optional[Callable[[str], None]] = None
        self.on_player_joined: Optional[Callable[[PlayerState], None]] = None
        self.on_player_left: Optional[Callable[[str], None]] = None
        self.on_room_updated: Optional[Callable[[Room], None]] = None
        self.on_chat_received: Optional[Callable[[str, str, str], None]] = None
        self.on_game_state: Optional[Callable[[dict], None]] = None
    
    @property
    def is_connected(self) -> bool:
        return self._connected
    
    async def connect(self, host: str = "localhost", port: int = 8765) -> bool:
        """连接到游戏服务器"""
        self.server_url = f"ws://{host}:{port}"
        
        try:
            logger.info(f"正在连接到 {self.server_url}...")
            self.websocket = await asyncio.wait_for(
                asyncio.get_event_loop().create_connection(
                    lambda: WebSocketProtocol(self),
                    host, port
                ),
                timeout=10.0
            )
            self._connected = True
            self._reconnect_count = 0
            logger.info("连接成功!")
            
            # 启动接收和心跳任务
            self._running = True
            self._receive_task = asyncio.create_task(self._receive_loop())
            self._heartbeat_task = asyncio.create_task(self.start_heartbeat())
            
            if self.on_connect:
                self.on_connect()
            
            return True
            
        except asyncio.TimeoutError:
            logger.error("连接超时")
            await self._attempt_reconnect()
            return False
        except Exception as e:
            logger.error(f"连接失败: {e}")
            await self._attempt_reconnect()
            return False
    
    async def _attempt_reconnect(self):
        """尝试重新连接"""
        if self._reconnect_count < self._max_reconnect_attempts:
            self._reconnect_count += 1
            logger.info(f"尝试重新连接 ({self._reconnect_count}/{self._max_reconnect_attempts})...")
            await asyncio.sleep(self._reconnect_delay)
            await self.connect()
        else:
            logger.error("达到最大重连次数，放弃连接")
            if self.on_error:
                self.on_error("无法连接到服务器")
    
    async def disconnect(self):
        """断开连接"""
        self._running = False
        
        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
        
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        if self.websocket:
            self.websocket.close()
        
        self._connected = False
        logger.info("已断开连接")
        
        if self.on_disconnect:
            self.on_disconnect()
    
    async def send(self, message: GameMessage):
        """发送消息到服务器"""
        if not self._connected or not self.websocket:
            logger.warning("未连接到服务器")
            return
        
        try:
            data = message.to_json()
            self.websocket.write(data.encode())
            await self.websocket.drain()
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            self._connected = False
    
    async def _receive_loop(self):
        """接收消息循环"""
        try:
            while self._running:
                try:
                    data = await self.websocket.read(4096)
                    if not data:
                        break
                    
                    message = GameMessage.from_json(data.decode())
                    await self.handle_message(message)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"接收消息错误: {e}")
                    break
                    
        except asyncio.CancelledError:
            pass
        finally:
            self._connected = False
    
    async def handle_message(self, message: GameMessage):
        """处理接收到的消息"""
        msg_type = MessageType(message.type)
        
        if msg_type == MessageType.PLAYER_DATA:
            # 处理玩家数据
            player_data = message.payload.get("player", {})
            self.player_id = player_data.get("player_id")
            self.sync_manager.set_local_player(
                self.player_id,
                player_data.get("name", "未知")
            )
            
        elif msg_type == MessageType.PLAYER_UPDATE:
            # 处理玩家更新
            player_data = message.payload
            self.sync_manager.apply_remote_update(
                message.player_id,
                player_data
            )
            
        elif msg_type == MessageType.ROOM_INFO:
            # 处理房间信息
            room_data = message.payload
            self.current_room = Room(
                room_id=room_data.get("room_id"),
                name=room_data.get("name"),
                host_id=room_data.get("host_id"),
                max_players=room_data.get("max_players", 10),
                state=RoomState(room_data.get("state", "waiting"))
            )
            if self.on_room_updated:
                self.on_room_updated(self.current_room)
            
        elif msg_type == MessageType.CHAT:
            # 处理聊天消息
            sender = message.payload.get("sender", "系统")
            content = message.payload.get("content", "")
            msg_type_chat = message.payload.get("msg_type", "public")
            if self.on_chat_received:
                self.on_chat_received(sender, content, msg_type_chat)
            
        elif msg_type == MessageType.GAME_STATE:
            # 处理游戏状态同步
            state = message.payload
            if self.on_game_state:
                self.on_game_state(state)
            
        elif msg_type == MessageType.ERROR:
            # 处理错误消息
            error_msg = message.payload.get("message", "未知错误")
            logger.error(f"服务器错误: {error_msg}")
            if self.on_error:
                self.on_error(error_msg)
        
        # 调用通用处理器
        handler = self.handlers.get(msg_type)
        if handler:
            await handler(message)
    
    # ==================== 客户端操作方法 ====================
    
    async def login(self, player_name: str) -> bool:
        """登录"""
        self.player_name = player_name
        message = create_sync_message(
            MessageType.LOGIN,
            {"name": player_name}
        )
        await self.send(message)
        return True
    
    async def create_room(self, room_name: str, max_players: int = 10) -> bool:
        """创建房间"""
        message = create_sync_message(
            MessageType.CREATE_ROOM,
            {"name": room_name, "max_players": max_players},
            self.player_id
        )
        await self.send(message)
        return True
    
    async def join_room(self, room_id: str) -> bool:
        """加入房间"""
        message = create_sync_message(
            MessageType.JOIN_ROOM,
            {"room_id": room_id},
            self.player_id
        )
        await self.send(message)
        return True
    
    async def leave_room(self) -> bool:
        """离开房间"""
        message = create_sync_message(
            MessageType.LEAVE_ROOM,
            {},
            self.player_id
        )
        await self.send(message)
        self.current_room = None
        return True
    
    async def send_chat(self, content: str, msg_type: str = "public") -> bool:
        """发送聊天消息"""
        message = create_sync_message(
            MessageType.CHAT,
            {"content": content, "msg_type": msg_type},
            self.player_id
        )
        await self.send(message)
        return True
    
    async def send_action(self, action_type: str, action_data: dict) -> bool:
        """发送玩家动作（同步用）"""
        if not self.sync_manager.local_state:
            return False
        
        self.sync_manager.update_local_state(**action_data)
        
        message = create_sync_message(
            MessageType.ACTION,
            {
                "action_type": action_type,
                "data": action_data,
                "player_state": self.sync_manager.local_state.to_dict()
            },
            self.player_id
        )
        await self.send(message)
        return True
    
    async def sync_state(self) -> bool:
        """同步游戏状态"""
        if not self.sync_manager.should_sync():
            return False
        
        message = create_sync_message(
            MessageType.SYNC,
            {
                "state": self.sync_manager.get_state_snapshot()
            },
            self.player_id
        )
        await self.send(message)
        self.sync_manager.mark_synced()
        return True


class WebSocketProtocol(asyncio.Protocol):
    """WebSocket 协议处理"""
    
    def __init__(self, client: GameClient):
        self.client = client
        self.transport = None
        self._buffer = b""
    
    def connection_made(self, transport):
        self.transport = transport
        logger.info("WebSocket 连接已建立")
    
    def data_received(self, data):
        self._buffer += data
        
        # 简单处理：假设每条消息以换行符结束
        while b"\n" in self._buffer:
            line, self._buffer = self._buffer.split(b"\n", 1)
            if line:
                try:
                    message = GameMessage.from_json(line.decode())
                    asyncio.create_task(self.client.handle_message(message))
                except Exception as e:
                    logger.error(f"解析消息失败: {e}")
    
    def connection_lost(self, exc):
        logger.info("WebSocket 连接断开")
        self.client._connected = False
        if self.client.on_disconnect:
            self.client.on_disconnect()


# 导出
__all__ = ['GameClient']
