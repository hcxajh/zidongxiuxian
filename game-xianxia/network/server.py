"""
修仙游戏 - WebSocket 服务器实现
处理多玩家连接、游戏状态同步、房间管理
"""

import asyncio
import json
import logging
import uuid
import time
from typing import Dict, Optional, Set
from dataclasses import dataclass, field

from network import (
    MessageType, GameMessage, PlayerState, Room, RoomState,
    create_sync_message, SyncManager
)


logger = logging.getLogger(__name__)


@dataclass
class ConnectedPlayer:
    """已连接的玩家"""
    player_id: str
    name: str
    transport: asyncio.Transport
    room_id: Optional[str] = None
    last_active: float = field(default_factory=time.time)
    sync_manager: SyncManager = field(default_factory=SyncManager)


class GameServer:
    """游戏服务器 - 管理所有连接和游戏状态"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self.server: Optional[asyncio.Server] = None
        
        # 玩家管理
        self.players: Dict[str, ConnectedPlayer] = {}
        self.player_names: Dict[str, str] = {}  # name -> player_id
        
        # 房间管理
        self.rooms: Dict[str, Room] = {}
        
        # 事件处理
        self.event_handlers: Dict[MessageType, list] = {
            msg_type: [] for msg_type in MessageType
        }
        
        # 服务器配置
        self.max_rooms = 100
        self.max_players_per_room = 20
        self.player_timeout = 300  # 玩家超时（秒）
        self.state_sync_interval = 1.0  # 状态同步间隔（秒）
        
        # 统计
        self.total_connections = 0
        self.start_time = time.time()
    
    async def start(self):
        """启动服务器"""
        self.server = await asyncio.start_server(
            self._handle_client,
            self.host,
            self.port
        )
        
        addr = self.server.sockets[0].getsockname()
        logger.info(f"游戏服务器已启动: {addr}")
        
        # 启动定期任务
        asyncio.create_task(self._cleanup_loop())
        asyncio.create_task(self._sync_loop())
        
        # 保持服务器运行
        async with self.server:
            await self.server.serve_forever()
    
    async def stop(self):
        """停止服务器"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        logger.info("游戏服务器已停止")
    
    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """处理客户端连接"""
        addr = writer.get_extra_info('peername')
        logger.info(f"新连接: {addr}")
        
        player_id = str(uuid.uuid4())
        player = ConnectedPlayer(
            player_id=player_id,
            name=f"玩家{len(self.players) + 1}",
            transport=writer
        )
        
        self.players[player_id] = player
        self.total_connections += 1
        
        try:
            # 发送欢迎消息
            await self._send_to_client(writer, GameMessage(
                type=MessageType.SYSTEM.value,
                payload={
                    "message": f"欢迎来到修仙世界！您的ID: {player_id}",
                    "player_id": player_id
                }
            ))
            
            # 发送玩家数据
            await self._send_to_client(writer, GameMessage(
                type=MessageType.PLAYER_DATA.value,
                payload={
                    "player": {
                        "player_id": player_id,
                        "name": player.name
                    }
                },
                player_id=player_id
            ))
            
            # 处理消息
            while True:
                try:
                    data = await asyncio.wait_for(reader.readline(), timeout=60.0)
                    if not data:
                        break
                    
                    message = GameMessage.from_json(data.decode())
                    await self._handle_message(player, message)
                    
                except asyncio.TimeoutError:
                    # 检查心跳
                    if time.time() - player.last_active > self.player_timeout:
                        logger.info(f"玩家 {player_id} 超时断开")
                        break
                except Exception as e:
                    logger.error(f"处理消息错误: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"客户端错误: {e}")
        finally:
            # 清理玩家
            if player.room_id:
                await self._remove_player_from_room(player)
            
            if player_id in self.players:
                del self.players[player_id]
            
            if player.name in self.player_names:
                del self.player_names[player.name]
            
            writer.close()
            await writer.wait_closed()
            logger.info(f"连接断开: {addr}")
    
    async def _handle_message(self, player: ConnectedPlayer, message: GameMessage):
        """处理客户端消息"""
        player.last_active = time.time()
        msg_type = MessageType(message.type)
        
        if msg_type == MessageType.LOGIN:
            await self._handle_login(player, message)
        
        elif msg_type == MessageType.HEARTBEAT:
            # 心跳响应
            pass
        
        elif msg_type == MessageType.CREATE_ROOM:
            await self._handle_create_room(player, message)
        
        elif msg_type == MessageType.JOIN_ROOM:
            await self._handle_join_room(player, message)
        
        elif msg_type == MessageType.LEAVE_ROOM:
            await self._handle_leave_room(player)
        
        elif msg_type == MessageType.ROOM_LIST:
            await self._handle_room_list(player)
        
        elif msg_type == MessageType.CHAT:
            await self._handle_chat(player, message)
        
        elif msg_type == MessageType.ACTION:
            await self._handle_action(player, message)
        
        elif msg_type == MessageType.SYNC:
            await self._handle_sync(player, message)
        
        # 调用事件处理器
        handlers = self.event_handlers.get(msg_type, [])
        for handler in handlers:
            try:
                await handler(player, message)
            except Exception as e:
                logger.error(f"事件处理器错误: {e}")
    
    # ==================== 消息处理 ====================
    
    async def _handle_login(self, player: ConnectedPlayer, message: GameMessage):
        """处理登录"""
        name = message.payload.get("name", "未知修士")
        
        # 检查名称是否已存在
        if name in self.player_names:
            name = f"{name}_{len(self.players)}"
        
        player.name = name
        self.player_names[name] = player.player_id
        player.sync_manager.set_local_player(player.player_id, name)
        
        await self._send_to_client(player.transport, GameMessage(
            type=MessageType.PLAYER_DATA.value,
            payload={
                "player": {
                    "player_id": player.player_id,
                    "name": name
                }
            },
            player_id=player.player_id
        ))
        
        # 广播玩家列表更新
        await self._broadcast_player_list()
    
    async def _handle_create_room(self, player: ConnectedPlayer, message: GameMessage):
        """处理创建房间"""
        if len(self.rooms) >= self.max_rooms:
            await self._send_error(player.transport, "房间已满")
            return
        
        room_name = message.payload.get("name", f"{player.name}的房间")
        max_players = message.payload.get("max_players", 10)
        
        room_id = str(uuid.uuid4())[:8]
        room = Room(
            room_id=room_id,
            name=room_name,
            host_id=player.player_id,
            max_players=max_players
        )
        
        self.rooms[room_id] = room
        await self._add_player_to_room(player, room_id)
        
        # 发送房间信息
        await self._send_to_client(player.transport, GameMessage(
            type=MessageType.ROOM_INFO.value,
            payload=room.to_dict(),
            player_id=player.player_id
        ))
        
        logger.info(f"玩家 {player.name} 创建了房间: {room_name}")
    
    async def _handle_join_room(self, player: ConnectedPlayer, message: GameMessage):
        """处理加入房间"""
        room_id = message.payload.get("room_id")
        
        if not room_id or room_id not in self.rooms:
            await self._send_error(player.transport, "房间不存在")
            return
        
        room = self.rooms[room_id]
        
        if len(room.players) >= room.max_players:
            await self._send_error(player.transport, "房间已满")
            return
        
        # 离开当前房间
        if player.room_id:
            await self._remove_player_from_room(player)
        
        # 加入新房间
        await self._add_player_to_room(player, room_id)
        
        # 通知房间内其他玩家
        await self._broadcast_to_room(room_id, GameMessage(
            type=MessageType.SYSTEM.value,
            payload={"message": f"{player.name} 进入了房间"},
            player_id=player.player_id
        ), exclude_player=player.player_id)
    
    async def _handle_leave_room(self, player: ConnectedPlayer):
        """处理离开房间"""
        if player.room_id:
            await self._remove_player_from_room(player)
    
    async def _handle_room_list(self, player: ConnectedPlayer):
        """处理获取房间列表"""
        room_list = [room.to_dict() for room in self.rooms.values()]
        
        await self._send_to_client(player.transport, GameMessage(
            type=MessageType.ROOM_LIST.value,
            payload={"rooms": room_list},
            player_id=player.player_id
        ))
    
    async def _handle_chat(self, player: ConnectedPlayer, message: GameMessage):
        """处理聊天消息"""
        content = message.payload.get("content", "")
        msg_type = message.payload.get("msg_type", "public")
        
        chat_msg = GameMessage(
            type=MessageType.CHAT.value,
            payload={
                "sender": player.name,
                "content": content,
                "msg_type": msg_type,
                "timestamp": time.time()
            },
            player_id=player.player_id
        )
        
        if msg_type == "whisper":
            # 私聊
            target_name = message.payload.get("target")
            target_id = self.player_names.get(target_name)
            if target_id and target_id in self.players:
                await self._send_to_client(
                    self.players[target_id].transport,
                    chat_msg
                )
        elif player.room_id:
            # 房间内广播
            await self._broadcast_to_room(player.room_id, chat_msg)
        else:
            # 全局广播
            await self._broadcast(chat_msg)
    
    async def _handle_action(self, player: ConnectedPlayer, message: GameMessage):
        """处理玩家动作"""
        if not player.room_id:
            return
        
        room = self.rooms.get(player.room_id)
        if not room:
            return
        
        # 更新玩家状态
        action_type = message.payload.get("action_type")
        action_data = message.payload.get("data", {})
        player_state_data = message.payload.get("player_state", {})
        
        # 更新本地状态
        player.sync_manager.update_local_state(**action_data)
        
        # 广播给房间内其他玩家
        await self._broadcast_to_room(player.room_id, GameMessage(
            type=MessageType.PLAYER_UPDATE.value,
            payload=player_state_data,
            player_id=player.player_id
        ), exclude_player=player.player_id)
    
    async def _handle_sync(self, player: ConnectedPlayer, message: GameMessage):
        """处理状态同步"""
        if not player.room_id:
            return
        
        state = message.payload.get("state", {})
        
        # 广播状态给房间内其他玩家
        await self._broadcast_to_room(player.room_id, GameMessage(
            type=MessageType.GAME_STATE.value,
            payload=state,
            player_id=player.player_id
        ), exclude_player=player.player_id)
    
    # ==================== 辅助方法 ====================
    
    async def _send_to_client(self, transport: asyncio.Transport, message: GameMessage):
        """发送消息到客户端"""
        try:
            data = message.to_json() + "\n"
            transport.write(data.encode())
            await transport.drain()
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
    
    async def _send_error(self, transport: asyncio.Transport, error_msg: str):
        """发送错误消息"""
        await self._send_to_client(transport, GameMessage(
            type=MessageType.ERROR.value,
            payload={"message": error_msg}
        ))
    
    async def _broadcast(self, message: GameMessage):
        """广播消息给所有玩家"""
        for player in self.players.values():
            await self._send_to_client(player.transport, message)
    
    async def _broadcast_to_room(self, room_id: str, message: GameMessage, exclude_player: str = None):
        """广播消息给房间内玩家"""
        room = self.rooms.get(room_id)
        if not room:
            return
        
        for player_id in room.players:
            if player_id == exclude_player:
                continue
            if player_id in self.players:
                await self._send_to_client(
                    self.players[player_id].transport,
                    message
                )
    
    async def _add_player_to_room(self, player: ConnectedPlayer, room_id: str):
        """添加玩家到房间"""
        room = self.rooms.get(room_id)
        if not room:
            return
        
        player_state = PlayerState(
            player_id=player.player_id,
            name=player.name
        )
        room.players[player.player_id] = player_state
        player.room_id = room_id
        
        logger.info(f"玩家 {player.name} 加入房间 {room.name}")
    
    async def _remove_player_from_room(self, player: ConnectedPlayer):
        """从房间移除玩家"""
        room_id = player.room_id
        if not room_id or room_id not in self.rooms:
            return
        
        room = self.rooms[room_id]
        
        if player.player_id in room.players:
            del room.players[player.player_id]
        
        # 如果房间为空，删除房间
        if not room.players:
            del self.rooms[room_id]
            logger.info(f"房间 {room_id} 已删除（无玩家）")
        # 如果房主离开，转移房主
        elif room.host_id == player.player_id and room.players:
            room.host_id = list(room.players.keys())[0]
            await self._broadcast_to_room(room_id, GameMessage(
                type=MessageType.SYSTEM.value,
                payload={"message": f"房主已离开，新房主: {room.players[room.host_id].name}"}
            ))
        
        player.room_id = None
        
        # 通知房间内其他玩家
        await self._broadcast_to_room(room_id, GameMessage(
            type=MessageType.SYSTEM.value,
            payload={"message": f"{player.name} 离开了房间"}
        ))
    
    async def _broadcast_player_list(self):
        """广播玩家列表更新"""
        player_list = [
            {"player_id": p.player_id, "name": p.name, "room_id": p.room_id}
            for p in self.players.values()
        ]
        
        await self._broadcast(GameMessage(
            type=MessageType.PLAYER_LIST.value,
            payload={"players": player_list}
        ))
    
    # ==================== 定期任务 ====================
    
    async def _cleanup_loop(self):
        """清理过期连接"""
        while True:
            await asyncio.sleep(60)
            
            current_time = time.time()
            to_remove = []
            
            for player_id, player in self.players.items():
                if current_time - player.last_active > self.player_timeout:
                    to_remove.append(player_id)
            
            for player_id in to_remove:
                player = self.players[player_id]
                if player.room_id:
                    await self._remove_player_from_room(player)
                
                player.transport.close()
                del self.players[player_id]
                
                if player.name in self.player_names:
                    del self.player_names[player.name]
    
    async def _sync_loop(self):
        """游戏状态同步循环"""
        while True:
            await asyncio.sleep(self.state_sync_interval)
            
            # 同步房间内所有玩家的状态
            for room in self.rooms.values():
                if room.state == RoomState.PLAYING:
                    # 广播完整的游戏状态
                    game_state = {
                        "room_id": room.room_id,
                        "players": {k: v.to_dict() for k, v in room.players.items()},
                        "timestamp": time.time()
                    }
                    
                    await self._broadcast_to_room(room.room_id, GameMessage(
                        type=MessageType.GAME_STATE.value,
                        payload=game_state
                    ))
    
    # ==================== 事件系统 ====================
    
    def on(self, event: MessageType, handler):
        """注册事件处理器"""
        self.event_handlers[event].append(handler)
    
    def get_stats(self) -> dict:
        """获取服务器统计"""
        return {
            "uptime": time.time() - self.start_time,
            "total_connections": self.total_connections,
            "online_players": len(self.players),
            "active_rooms": len(self.rooms),
            "total_players_served": self.total_connections
        }


# 导出
__all__ = ['GameServer', 'ConnectedPlayer']
