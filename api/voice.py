import json
import logging
from services.asr_service import asrHandle

from utils.result import Result

async def voiceRoute(ws):
    """
    WebSocket音频路由
    :param ws:
    :return:
    """
    try:
        async for message in ws:
            input_audio_bytes=message;
            logging.info("收到二进制音频：%s",len(input_audio_bytes))

            await asrHandle(input_audio_bytes, ws)

    except Exception as e:
        await ws.send(json.dumps(Result.error(f"服务器内部错误，报错信息为{str(e)}")))