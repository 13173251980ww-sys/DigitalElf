import json
from typing import Generator
from utils.config import GLOBAL_CONFIG
from utils.rag import load_vector_store,retrieve_relevant_docs,build_rag_prompt
from openai import OpenAI
from utils.result import Result
from myEnums.ResultTypeEnum import ResultTypeEnum
from services.emtion_service import emtionHandle
from services.tts_service import ttsHandle
import asyncio
import logging
import os

CLIENT=None

def create_llm_model():
    """
    创建并返回llm实例，使用全局变量缓存模型以避免重复加载
    """
    global CLIENT
    if CLIENT is None:
        CLIENT =OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=GLOBAL_CONFIG.get("llm",{}).get("base_url")
        )
    return CLIENT

def chat_with_llm(client,user_text:str)->Generator[str, None, None]:
    #加载向量库
    vector_store = load_vector_store()

    # rag检索增强
    relevant_docs = retrieve_relevant_docs(user_text, vector_store)
    prompt = build_rag_prompt(user_text, relevant_docs)
    if not relevant_docs:
        logging.warning("未检索到相关文档")

    logging.info("大模型思考回复中")
    res=client.chat.completions.create(
        model=GLOBAL_CONFIG.get("llm",{}).get("model"),
        messages=[
            {"role":"system","content":prompt},
            {"role":"user","content":user_text}
        ],
        temperature=GLOBAL_CONFIG.get("llm",{}).get("temperature"),
        stream=GLOBAL_CONFIG.get("llm",{}).get("stream")
    )

    for chunk in res:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content


async def llmHandle(user_text:str,ws):
    logging.info("进入大模型回复模块")

    logging.info("开始进行大模型模型配置")
    client=create_llm_model()

    #回复流
    reply_stream=chat_with_llm(client,user_text)

    #缓冲队列(给TTS消费)
    reply_queue=asyncio.Queue()

    #启动tts消费任务
    asyncio.create_task(ttsHandle(reply_queue,ws))

    #给TTS启动时间
    await asyncio.sleep(0)

    #完整回复文本(给情感分析)
    reply_text=""

    #流式发送回复
    for chunk in reply_stream:
        reply_text+=chunk
        await reply_queue.put(chunk) #放入队列供TTS消费
        logging.info(f"大模型回复为{chunk}")
        await ws.send(json.dumps(Result.success(type=ResultTypeEnum.REPLAY.value, data=chunk)))
        # 每次放入后让出控制权给TTS
        await asyncio.sleep(0)

    await reply_queue.put(None) #通知TTS消费结束

    #调用情绪处理
    await emtionHandle(reply_text,ws)

    #等待TTS发送完成
    await reply_queue.join()














