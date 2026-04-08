from flask import Flask
from utils.logger import setup_logging
from api.voice import voiceRoute
from utils.config import GLOBAL_CONFIG
from utils.rag import build_vector_store
import websockets
import logging
import asyncio
import threading

_ws_lock = threading.Lock()
_ws_thread = None

async def start_ws_server():
    """
    启动WebSocket服务器，监听
    """
    server = await websockets.serve(
        voiceRoute,
        GLOBAL_CONFIG.get("ws",{}).get("host"),
        GLOBAL_CONFIG.get("ws",{}).get("port"),
    )

    logging.info("WebSocket服务启动: ws://%s:%s",GLOBAL_CONFIG.get("ws",{}).get("host"),GLOBAL_CONFIG.get("ws",{}).get("port"))
    await server.wait_closed()

def run_ws():
    """
    启动 WebSocket 服务器，使用 asyncio 运行 start_ws_server 协程
    """
    try:
        asyncio.run(start_ws_server())
    except Exception:
        logging.exception("WebSocket服务启动失败")

def start_ws_background_once():
    """
    启动一次 WebSocket 后台线程，避免重复占用端口
    """
    global _ws_thread

    with _ws_lock:
        if _ws_thread is not None and _ws_thread.is_alive():
            return

        _ws_thread = threading.Thread(target=run_ws, daemon=True, name="ws-server")
        _ws_thread.start()

def create_app():
    """
    创建并配置 Flask 应用实例
    :return: 配置好的 Flask 应用实例
    """
    app = Flask(__name__)

    #设置日志
    setup_logging()

    app.config["JSON_AS_ASCII"] = False
    if hasattr(app, "json") and app.json is not None:
        app.json.ensure_ascii = False

    # `flask run` 走应用工厂路径，因此在这里启动 WS 线程
    start_ws_background_once()

    #将.txt存入向量数据库
    build_vector_store()

    return app

if __name__ == "__main__":
    app = create_app()

    app.run(host=GLOBAL_CONFIG.get("app",{}).get("host"), port=GLOBAL_CONFIG.get("app",{}).get("port"), debug=GLOBAL_CONFIG.get("app",{}).get("debug"))






