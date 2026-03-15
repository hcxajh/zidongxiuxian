#!/usr/bin/env python3
"""
修仙游戏 - 网络同步服务器启动脚本
用法:
    python server.py              # 启动服务器
    python server.py --client    # 启动客户端演示
"""

import asyncio
import argparse
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def main():
    parser = argparse.ArgumentParser(description="修仙游戏网络同步")
    parser.add_argument("--host", default="0.0.0.0", help="服务器地址")
    parser.add_argument("--port", type=int, default=8765, help="服务器端口")
    parser.add_argument("--client", action="store_true", help="启动客户端模式")
    parser.add_argument("--demo", action="store_true", help="运行演示")
    
    args = parser.parse_args()
    
    if args.client or args.demo:
        # 客户端模式
        from network.integration import run_network_client_demo
        await run_network_client_demo()
    else:
        # 服务器模式
        from network.integration import run_network_server
        await run_network_server(args.host, args.port)


if __name__ == "__main__":
    asyncio.run(main())
