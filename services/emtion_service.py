from transformers import pipeline
from utils.config import GLOBAL_CONFIG
from utils.result import Result
from myEnums.ResultTypeEnum import ResultTypeEnum
import logging
import json


CLASSIFIER=None

def create_llm_model():
    """
    创建并返回emotion分类器实例，使用全局变量缓存模型以避免重复加载
    """
    global CLASSIFIER
    if CLASSIFIER is None:
        CLASSIFIER=pipeline(task=GLOBAL_CONFIG.get("emotion",{}).get("task"), model=GLOBAL_CONFIG.get("emotion",{}).get("model"),
                            return_all_scores=GLOBAL_CONFIG.get("emotion",{}).get("return_all_scores"))

    return CLASSIFIER

async def emotion_handle(reply_text,ws):
    """
    情绪分类为:joy,sadness,anger,love,fear,anger,surprise.当情绪分析置信度小于0.7时，返回speak
    """
    classifier = create_llm_model()
    prediction = classifier(reply_text )

    label = prediction[0]['label']
    score = prediction[0]['score']

    logging.info(f"情感分析的结果为: {label}, 置信度: {score}")

    if score>=0.7:
        await ws.send(json.dumps(Result.success(type=ResultTypeEnum.EMOTION.value, data=label)))
    elif score<0.7:
        await ws.send(json.dumps(Result.success(type=ResultTypeEnum.EMOTION.value, data="speak")))







