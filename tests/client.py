import asyncio
import json
import logging

import websockets
import uuid
from pathlib import Path


async def send_audio(uri="ws://127.0.0.1:8765", audio_file="test.wav"):
    """最简单的音频发送客户端"""
    # 读取音频文件
    audio_path = Path(audio_file)
    if not audio_path.exists():
        print(f"文件不存在: {audio_file}")
        return

    audio_bytes = audio_path.read_bytes()
    print(f"读取音频: {audio_file}, 大小: {len(audio_bytes)} bytes")

    # 连接WebSocket
    async with websockets.connect(uri) as websocket:
        # 发送音频数据
        await websocket.send(audio_bytes)
        print(f"已发送音频数据")

        # 等待服务器响应
        while True:
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=30)
                if isinstance(response, bytes):
                    print(f"收到音频数据: {len(response)} bytes")
                else:
                    payload = json.loads(response)
                    print(f"收到响应: {payload}")

            except asyncio.TimeoutError:
                print("等待响应超时，退出")
                break
            except websockets.exceptions.ConnectionClosed:
                print("连接已关闭")
                break

# 运行
if __name__ == "__main__":
    asyncio.run(send_audio("ws://127.0.0.1:8765", "audio/test.wav"))