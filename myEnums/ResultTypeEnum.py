from enum import Enum


class ResultTypeEnum(Enum):
    """
    返回结果类型
    """

    REPLAY = "回复"
    EMOTION = "情绪"
    AUDIO = "音频"
