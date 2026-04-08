from utils.config import GLOBAL_CONFIG
from openai import OpenAI
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

def chat_with_llm(client,user_text:str):

    res=client.chat.completions.create(
        model=GLOBAL_CONFIG.get("llm",{}).get("model"),
        message={
            {"role":"system","content":prompt},
            {"role":"user","content":user_text}
        },
        temperature=GLOBAL_CONFIG.get("llm",{}).get("temperature")

    )

    return res


async def llmHandle(user_text:str,ws):
    logging.info("进入大模型回复模块")

    logging.info("开始进行大模型模型配置")
    client=create_llm_model()




