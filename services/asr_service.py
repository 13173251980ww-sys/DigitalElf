from funasr import AutoModel
from typing import Tuple
from utils.config import GLOBAL_CONFIG
from funasr.utils.postprocess_utils import rich_transcription_postprocess
import soundfile as sf
import numpy as np
import logging
from services.llm_service import llmHandle
import io

MODEL=None

def audio_bytes_to_waveform(audio_bytes: bytes) -> Tuple[np.ndarray, int]:
    """
    使用soundfile读取WAV字节数据
    :param audio_bytes: WAV音频字节
    :return: (波形数组, 采样率)
    """
    with io.BytesIO(audio_bytes) as buffer:
        audio, sr = sf.read(buffer, dtype='float32', always_2d=False)

        # 转换为单声道
        if audio.ndim == 2:
            audio = audio.mean(axis=1)

        return audio, sr

def create_funasr_model():
    """
    创建并返回FunASR模型实例，使用全局变量缓存模型以避免重复加载
    """
    global MODEL
    if MODEL is None:
        MODEL=AutoModel(
            model=GLOBAL_CONFIG.get("asr",{}).get("model"),
            vad_model=GLOBAL_CONFIG.get("asr",{}).get("vad_model"),
            vad_kwargs=GLOBAL_CONFIG.get("asr",{}).get("vad_kwargs",{}),
            device=GLOBAL_CONFIG.get("asr",{}).get("device"),
        )
    return MODEL

def generate_funasr_result(model: AutoModel,waveform):
    """"
    使用FunASR模型进行语音识别
    """
    return model.generate(
        input=waveform,
        cache={},
        language=GLOBAL_CONFIG.get("asr",{}).get("language"),
        use_itn=GLOBAL_CONFIG.get("asr",{}).get("use_itn"),
        batch_size_s=GLOBAL_CONFIG.get("asr",{}).get("batch_size_s"),
        merge_vad=GLOBAL_CONFIG.get("asr",{}).get("merge_vad"),
        merge_length_s=GLOBAL_CONFIG.get("asr",{}).get("merge_length_s")
    )

async def asrHandle(input_audio_bytes:bytes, ws):
    logging.info("进入语音转文字处理模块")

    waveform,sr=audio_bytes_to_waveform(input_audio_bytes)
    logging.info("已转成waveform，sr: %s len: %s seconds: %.2f", sr, waveform.shape[0], waveform.shape[0] / sr)

    logging.info("开始进行FunASR模型配置")
    model = create_funasr_model()

    logging.info("开始语音转文字")
    user_text = generate_funasr_result(model, waveform)

    # 文本清洗
    user_text = rich_transcription_postprocess(user_text[0]["text"])
    logging.info("ASR text: %s", user_text)

    await llmHandle(user_text, ws)


