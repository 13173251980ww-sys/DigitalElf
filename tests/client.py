import asyncio
import websockets
import uuid
from pathlib import Path


async def send_audio(uri="ws://127.0.0.1:8765", audio_file="test.wav"):
    """最简单的音频发送客户端"""

    # 生成会话ID
    session_id = uuid.uuid4().hex[:8]

    # 读取音频文件
    audio_path = Path(audio_file)
    if not audio_path.exists():
        print(f"文件不存在: {audio_file}")
        return

    audio_bytes = audio_path.read_bytes()
    print(f"读取音频: {audio_file}, 大小: {len(audio_bytes)} bytes")

    # 连接WebSocket
    async with websockets.connect(uri) as websocket:
        print(f"已连接到 {uri}, session_id={session_id}")

        # 发送音频数据
        await websocket.send(audio_bytes)
        print(f"已发送音频数据")

        # 等待服务器响应
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=10)
            print(f"收到响应: {response}")
        except asyncio.TimeoutError:
            print("等待响应超时")
        except Exception as e:
            print(f"接收响应失败: {e}")

# 运行
if __name__ == "__main__":
    asyncio.run(send_audio("ws://127.0.0.1:8765", "audio/test.wav"))