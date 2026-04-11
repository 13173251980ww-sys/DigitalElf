import asyncio
import logging
import requests
from utils.config import GLOBAL_CONFIG


async def send_tts_audio(text,ws):
    """
    流式调用VITS接口生成语音，直接通过WebSocket发送音频块
    :param text: 要转换为语音的文本
    """
    tts_config = GLOBAL_CONFIG.get("tts", {})
    url = tts_config.get("url")

    # POST 请求
    payload = {
        "text": text,
        "text_lang": tts_config.get("text_lang", "zh"),
        "ref_audio_path": tts_config.get("ref_audio_path", ""),
        "prompt_lang": tts_config.get("prompt_lang", "zh"),
        "prompt_text": tts_config.get("prompt_text", ""),
        "streaming_mode": tts_config.get("streaming_mode", True),
        "media_type": tts_config.get("media_type", "wav"),
    }

    logging.info(f"请求TTS接口，文本{text}")
    response = requests.post(
        url,
        json=payload,
        timeout=tts_config.get("timeout", 30)
    )

    await ws.send(response.content)


async def tts_handle(reply_queue, ws):
    logging.info("进入TTS模块")
    buffer = ""
    pending_tasks = []

    while True:
        tts_chunk = await reply_queue.get()
        logging.info(f"TTS开始消费文本块: {tts_chunk}")

        if tts_chunk is None:
            if buffer.strip():
                task = asyncio.create_task(send_tts_audio(buffer.strip(),ws))
                pending_tasks.append(task)

            # 等待所有任务完成
            if pending_tasks:
                await asyncio.gather(*pending_tasks, return_exceptions=True)
            reply_queue.task_done()
            break

        buffer += tts_chunk

        await asyncio.sleep(0)#让出调度给发送

        if any(p in buffer for p in ["。", "！", "？", ".", "!", "?"]):
            sentence = buffer.strip()
            buffer = ""
            if sentence:
                logging.info(f"请求TTS接口，文本{sentence}")
                task = asyncio.create_task(send_tts_audio(sentence,ws))
                pending_tasks.append(task)

        reply_queue.task_done()
