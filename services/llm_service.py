import json

from utils.config import GLOBAL_CONFIG
from utils.rag import load_vector_store,retrieve_relevant_docs,build_rag_prompt
from openai import OpenAI
from utils.result import Result
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
    #加载向量库
    vector_store = load_vector_store()

    # rag检索增强
    relevant_docs = retrieve_relevant_docs(user_text, vector_store)
    prompt = build_rag_prompt(user_text, relevant_docs)
    if not relevant_docs:
        logging.warning("未检索到相关文档")
        return "未找到相关知识"

    logging.info("大模型思考回复中")
    res=client.chat.completions.create(
        model=GLOBAL_CONFIG.get("llm",{}).get("model"),
        messages=[
            {"role":"system","content":prompt},
            {"role":"user","content":user_text}
        ],
        temperature=GLOBAL_CONFIG.get("llm",{}).get("temperature")
    )

    return res.choices[0].message.content


async def llmHandle(user_text:str,ws):
    logging.info("进入大模型回复模块")

    logging.info("开始进行大模型模型配置")
    client=create_llm_model()

    res=chat_with_llm(client,user_text)

    logging.info(f"大模型回复为{res}")

    await ws.send(json.dumps(Result.success(type="回复",data=res)))




