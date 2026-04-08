from dataclasses import dataclass, asdict
from typing import Any, Optional, Dict

@dataclass
class Result:
    """
    统一的API响应格式
    """
    code: int                 # 1 成功，0/其它 失败
    type: str                #响应类型(如:回复文本,情绪,音频)
    msg: Optional[str] = None # 错误信息
    data: Any = None          # 数据

    @staticmethod
    def success(type:str,data: Any = None) -> Dict[str, Any]:
        """成功：可带数据也可不带数据,必须传类型"""
        return asdict(Result(type=type,code=1, msg=None, data=data))

    @staticmethod
    def error(msg: str, code: int = 0, data: Any = None,type: str = "error",) -> Dict[str, Any]:
        """失败：默认 code=0，可自定义 code"""
        return asdict(Result(type=type,code=code, msg=msg, data=data))