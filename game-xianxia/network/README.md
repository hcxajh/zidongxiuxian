# 修仙游戏网络同步架构

## 概述

本模块为修仙游戏提供多玩家在线同步功能，支持实时多人交互。

## 架构设计

### 核心组件

```
┌─────────────────────────────────────────────────────────────┐
│                      游戏服务器 (GameServer)                 │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  玩家管理   │  │  房间管理   │  │  状态同步引擎       │ │
│  │ PlayerMgr   │  │  RoomMgr    │  │  StateSync          │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    WebSocket Server                         │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                      游戏客户端 (GameClient)                 │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ 连接管理   │  │ 消息队列   │  │  本地状态缓存       │ │
│  │ Connection │  │  MessageQ  │  │  LocalState        │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 消息类型

| 类型 | 方向 | 说明 |
|------|------|------|
| LOGIN | C→S | 玩家登录 |
| LOGOUT | C→S | 玩家登出 |
| CREATE_ROOM | C→S | 创建房间 |
| JOIN_ROOM | C→S | 加入房间 |
| LEAVE_ROOM | C→S | 离开房间 |
| CHAT | C↔S | 聊天消息 |
| ACTION | C→S | 玩家动作 |
| SYNC | C↔S | 状态同步 |
| GAME_STATE | S→C | 游戏状态广播 |
| PLAYER_UPDATE | S→C | 玩家数据更新 |
| HEARTBEAT | C↔S | 心跳保活 |

### 数据结构

#### PlayerState (玩家状态)

```python
{
    "player_id": "uuid",
    "name": "修士名称",
    "realm": "炼气期",
    "level": 1,
    "hp": 100.0,
    "max_hp": 100.0,
    "qi": 0.0,
    "max_qi": 100.0,
    "attack": 10,
    "defense": 5,
    "spirit_stones": 100,
    "x": 0.0,
    "y": 0.0,
    "status": "idle"
}
```

#### Room (房间)

```python
{
    "room_id": "uuid",
    "name": "房间名称",
    "host_id": "房主ID",
    "max_players": 10,
    "state": "waiting|playing|finished",
    "players": {...},
    "created_at": timestamp
}
```

## 使用方法

### 1. 启动服务器

```bash
cd game-xianxia
python server.py --host 0.0.0.0 --port 8765
```

### 2. 启动客户端演示

```bash
python server.py --client
```

### 3. 集成到游戏

```python
from network.integration import NetworkGameClient

# 连接服务器
client = NetworkGameClient()
await client.connect("localhost", 8765)

# 登录
await client.login("我的修士")

# 创建/加入房间
await client.create_room("我的洞府")
await client.join_room("room_id")

# 发送动作
await client.send_action("meditate", status="meditation")
await client.send_action("combat", status="combat")

# 聊天
await client.send_chat("各位修士好!")

# 断开
await client.disconnect()
```

## 同步策略

### 1. 状态同步 (State Synchronization)

- **全量同步**: 定期发送完整游戏状态
- **增量同步**: 只发送变更的数据
- **插值**: 客户端对收到的状态进行平滑过渡

### 2. 动作同步 (Action Synchronization)

- 玩家动作立即发送给服务器
- 服务器广播给房间内所有玩家
- 本地先执行动作，再等待服务器确认

### 3. 心跳保活

- 客户端每30秒发送一次心跳
- 服务器检测超时玩家并清理

## 扩展功能

### 计划中

- [ ] P2P 直连支持
- [ ] 房间密码保护
- [ ] 观战模式
- [ ] 排行榜系统
- [ ] 宗门/帮派系统同步

## 技术栈

- Python 3.10+
- asyncio (异步IO)
- WebSocket (实时通信)

## 文件结构

```
network/
├── __init__.py      # 核心数据类型和基类
├── client.py        # WebSocket 客户端
├── server.py        # 游戏服务器
├── integration.py   # 游戏集成接口
└── README.md       # 本文档
```
