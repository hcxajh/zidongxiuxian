"""
修仙游戏 - 网络模式集成
将网络同步功能集成到游戏主程序
"""

import asyncio
import sys
from typing import Optional
from network import GameClient, MessageType, GameMessage, PlayerState


class NetworkGameClient:
    """网络模式游戏客户端 - 集成到现有游戏"""
    
    def __init__(self, server_url: str = "ws://localhost:8765"):
        self.client = GameClient(server_url)
        self.server_url = server_url
        self._connected = False
        self._current_player_id: Optional[str] = None
        
        # 设置回调
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_error = self._on_error
        self.client.on_chat_received = self._on_chat_received
        self.client.on_room_updated = self._on_room_updated
    
    @property
    def is_connected(self) -> bool:
        return self.client.is_connected
    
    async def connect(self, host: str = "localhost", port: int = 8765) -> bool:
        """连接到服务器"""
        self.server_url = f"ws://{host}:{port}"
        return await self.client.connect(host, port)
    
    async def disconnect(self):
        """断开连接"""
        await self.client.disconnect()
    
    async def login(self, player_name: str) -> bool:
        """登录游戏"""
        return await self.client.login(player_name)
    
    async def create_room(self, room_name: str) -> bool:
        """创建房间"""
        return await self.client.create_room(room_name)
    
    async def join_room(self, room_id: str) -> bool:
        """加入房间"""
        return await self.client.join_room(room_id)
    
    async def leave_room(self) -> bool:
        """离开房间"""
        return await self.client.leave_room()
    
    async def send_chat(self, content: str) -> bool:
        """发送聊天消息"""
        return await self.client.send_chat(content)
    
    async def send_action(self, action_type: str, **kwargs) -> bool:
        """发送玩家动作"""
        return await self.client.send_action(action_type, kwargs)
    
    # ==================== 回调处理 ====================
    
    def _on_connect(self):
        """连接成功回调"""
        self._connected = True
        print("\n✅ 已连接到游戏服务器!")
    
    def _on_disconnect(self):
        """断开连接回调"""
        self._connected = False
        print("\n⚠️ 与服务器的连接已断开")
    
    def _on_error(self, error_msg: str):
        """错误回调"""
        print(f"\n❌ 错误: {error_msg}")
    
    def _on_chat_received(self, sender: str, content: str, msg_type: str):
        """收到聊天消息回调"""
        if msg_type == "public":
            print(f"\n[{sender}]: {content}")
        elif msg_type == "whisper":
            print(f"\n[私聊] {sender}: {content}")
    
    def _on_room_updated(self, room):
        """房间更新回调"""
        print(f"\n🏠 房间已更新: {room.name}")
        print(f"   玩家数量: {len(room.players)}/{room.max_players}")


async def run_network_server(host: str = "0.0.0.0", port: int = 8765):
    """运行网络服务器"""
    from network.server import GameServer
    
    server = GameServer(host=host, port=port)
    print(f"🚀 启动修仙游戏服务器: {host}:{port}")
    print("按 Ctrl+C 停止服务器")
    
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务器...")
        await server.stop()


async def run_network_client_demo():
    """运行网络客户端演示"""
    client = NetworkGameClient()
    
    print("=" * 50)
    print("       仙途 - 网络模式演示")
    print("=" * 50)
    
    # 连接服务器
    print("\n正在连接服务器...")
    if not await client.connect():
        print("连接失败!")
        return
    
    # 登录
    player_name = input("请输入角色名称: ").strip() or "测试修士"
    await client.login(player_name)
    
    # 主循环
    while client.is_connected:
        print("\n" + "=" * 30)
        print("【网络模式菜单】")
        print("1. 创建房间")
        print("2. 加入房间")
        print("3. 查看房间列表")
        print("4. 发送聊天")
        print("5. 发送动作")
        print("0. 退出")
        
        choice = input("\n请选择: ").strip()
        
        if choice == "1":
            room_name = input("输入房间名称: ").strip() or f"{player_name}的房间"
            await client.create_room(room_name)
            print(f"✅ 房间 '{room_name}' 创建成功!")
        
        elif choice == "2":
            room_id = input("输入房间ID: ").strip()
            if room_id:
                await client.join_room(room_id)
                print(f"✅ 加入房间成功!")
        
        elif choice == "3":
            print("\n📋 房间列表功能开发中...")
        
        elif choice == "4":
            msg = input("输入消息: ").strip()
            if msg:
                await client.send_chat(msg)
        
        elif choice == "5":
            print("\n动作: 1.打坐 2.战斗 3.移动")
            action_choice = input("选择: ").strip()
            if action_choice == "1":
                await client.send_action("meditate", status="meditation")
            elif action_choice == "2":
                await client.send_action("combat", status="combat")
            elif action_choice == "3":
                await client.send_action("move", x=100, y=200)
        
        elif choice == "0":
            break
    
    await client.disconnect()
    print("👋 已断开连接")


# ==================== 单机模式网络支持 ====================

class HybridGameMode:
    """混合游戏模式 - 支持单机和网络对战"""
    
    def __init__(self):
        self.client: Optional[NetworkGameClient] = None
        self.server_process = None
        self.is_host = False
    
    async def start_as_client(self, host: str = "localhost", port: int = 8765):
        """作为客户端启动"""
        self.client = NetworkGameClient()
        
        print(f"正在连接到 {host}:{port}...")
        if await self.client.connect(host, port):
            print("连接成功!")
            return True
        return False
    
    async def start_as_host(self, port: int = 8765):
        """作为主机启动（启动内置服务器）"""
        import subprocess
        
        # 启动服务器进程
        self.server_process = subprocess.Popen(
            [sys.executable, "-m", "network.server"],
            cwd="/Users/huacuo/.openclaw/workspace-cos/game-xianxia"
        )
        
        # 等待服务器启动
        await asyncio.sleep(2)
        
        # 连接到自己启动的服务器
        self.client = NetworkGameClient()
        self.is_host = True
        
        return await self.client.connect("localhost", port)
    
    async def stop(self):
        """停止"""
        if self.client:
            await self.client.disconnect()
        
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()


# 导出
__all__ = [
    'NetworkGameClient',
    'run_network_server', 
    'run_network_client_demo',
    'HybridGameMode'
]
