"""
修仙游戏 - 网络同步模块
支持多玩家在线同步功能
"""

import json
import asyncio
import uuid
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod


class MessageType(Enum):
    """消息类型"""
    # 认证
    LOGIN = "login"
    LOGOUT = "logout"
    REGISTER = "register"
    
    # 玩家数据
    PLAYER_DATA = "player_data"
    PLAYER_UPDATE = "player_update"
    PLAYER_LIST = "player_list"
    
    # 房间/大厅
    CREATE_ROOM = "create_room"
    JOIN_ROOM = "join_room"
    LEAVE_ROOM = "leave_room"
    ROOM_LIST = "room_list"
    ROOM_INFO = "room_info"
    
    # 游戏同步
    GAME_STATE = "game_state"
    ACTION = "action"
    SYNC = "sync"
    
    # 社交
    CHAT = "chat"
    WHISPER = "whisper"
    
    # 系统
    HEARTBEAT = "heartbeat"
    ERROR = "error"
    SYSTEM = "system"


class RoomState(Enum):
    """房间状态"""
    WAITING = "waiting"       # 等待中
    PLAYING = "playing"       # 游戏中
    FINISHED = "finished"     # 已结束


@dataclass
class PlayerState:
    """玩家状态（网络同步用）"""
    player_id: str
    name: str
    realm: str = "凡人"
    level: int = 1
    hp: float = 100.0
    max_hp: float = 100.0
    qi: float = 0.0
    max_qi: float = 100.0
    attack: int = 10
    defense: int = 5
    spirit_stones: int = 100
    x: float = 0.0           # 位置X
    y: float = 0.0           # 位置Y
    status: str = "idle"      # idle, combat, meditation
    last_update: float = field(default_factory=time.time)
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PlayerState':
        return cls(**data)


@dataclass
class Room:
    """游戏房间"""
    room_id: str
    name: str
    host_id: str
    max_players: int = 10
    state: RoomState = RoomState.WAITING
    players: Dict[str, PlayerState] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> dict:
        return {
            "room_id": self.room_id,
            "name": self.name,
            "host_id": self.host_id,
            "max_players": self.max_players,
            "state": self.state.value,
            "players": {k: v.to_dict() for k, v in self.players.items()},
            "player_count": len(self.players),
            "created_at": self.created_at
        }


@dataclass
class GameMessage:
    """网络消息"""
    type: str
    payload: dict = field(default_factory=dict)
    player_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def to_json(self) -> str:
        return json.dumps({
            "type": self.type,
            "payload": self.payload,
            "player_id": self.player_id,
            "timestamp": self.timestamp,
            "message_id": self.message_id
        })
    
    @classmethod
    def from_json(cls, data: str) -> 'GameMessage':
        obj = json.loads(data)
        return cls(
            type=obj["type"],
            payload=obj.get("payload", {}),
            player_id=obj.get("player_id"),
            timestamp=obj.get("timestamp", time.time()),
            message_id=obj.get("message_id", str(uuid.uuid4()))
        )


class NetworkSyncBase(ABC):
    """网络同步基类"""
    
    def __init__(self):
        self.handlers: Dict[MessageType, Callable] = {}
        self._running = False
    
    @abstractmethod
    async def connect(self, host: str, port: int) -> bool:
        """连接服务器"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """断开连接"""
        pass
    
    @abstractmethod
    async def send(self, message: GameMessage):
        """发送消息"""
        pass
    
    def register_handler(self, msg_type: MessageType, handler: Callable):
        """注册消息处理器"""
        self.handlers[msg_type] = handler
    
    async def handle_message(self, message: GameMessage):
        """处理接收到的消息"""
        msg_type = MessageType(message.type)
        handler = self.handlers.get(msg_type)
        if handler:
            await handler(message)
        else:
            print(f"[Network] 未处理的消息类型: {message.type}")
    
    async def start_heartbeat(self, interval: float = 30.0):
        """启动心跳"""
        while self._running:
            await asyncio.sleep(interval)
            await self.send(GameMessage(
                type=MessageType.HEARTBEAT.value,
                payload={"time": time.time()}
            ))


class SyncManager:
    """同步管理器 - 处理游戏状态的同步"""
    
    def __init__(self):
        self.local_state: Optional[PlayerState] = None
        self.remote_states: Dict[str, PlayerState] = {}
        self.pending_updates: List[dict] = []
        self.last_sync_time: float = 0
        self.sync_interval: float = 1.0  # 同步间隔（秒）
    
    def set_local_player(self, player_id: str, name: str):
        """设置本地玩家"""
        self.local_state = PlayerState(player_id=player_id, name=name)
    
    def update_local_state(self, **kwargs):
        """更新本地状态"""
        if self.local_state:
            for key, value in kwargs.items():
                if hasattr(self.local_state, key):
                    setattr(self.local_state, key, value)
            self.local_state.last_update = time.time()
    
    def apply_remote_update(self, player_id: str, data: dict):
        """应用远程玩家更新"""
        if player_id in self.remote_states:
            for key, value in data.items():
                if hasattr(self.remote_states[player_id], key):
                    setattr(self.remote_states[player_id], key, value)
            self.remote_states[player_id].last_update = time.time()
        else:
            self.remote_states[player_id] = PlayerState.from_dict(data)
    
    def get_state_snapshot(self) -> dict:
        """获取状态快照"""
        return {
            "local": self.local_state.to_dict() if self.local_state else None,
            "remote": {k: v.to_dict() for k, v in self.remote_states.items()},
            "timestamp": time.time()
        }
    
    def should_sync(self) -> bool:
        """检查是否需要同步"""
        return time.time() - self.last_sync_time >= self.sync_interval
    
    def mark_synced(self):
        """标记已同步"""
        self.last_sync_time = time.time()


def create_sync_message(msg_type: MessageType, payload: dict, player_id: str = None) -> GameMessage:
    """创建同步消息的辅助函数"""
    return GameMessage(type=msg_type.value, payload=payload, player_id=player_id)


# 导出
__all__ = [
    'MessageType',
    'RoomState', 
    'PlayerState',
    'Room',
    'GameMessage',
    'NetworkSyncBase',
    'SyncManager',
    'create_sync_message'
]
