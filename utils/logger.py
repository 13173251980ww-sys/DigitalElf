from pathlib import Path
from datetime import datetime
import logging
import sys

# 新增：颜色格式器类
class ColoredFormatter(logging.Formatter):
    def format(self, record):
        color_map = {
            logging.INFO: '\033[32m',     # 绿色
            logging.WARNING: '\033[33m',  # 黄色
            logging.ERROR: '\033[31m',    # 红色
        }
        color = color_map.get(record.levelno, '')
        if color:
            record.levelname = f"{color}{record.levelname}\033[0m"
        return super().format(record)

def get_daily_log_file_path() -> str:
    """
    获取每天的日志文件路径，日志文件保存在项目根目录下的logs文件夹中，文件名格式为"YYYY-MM-DD_HH-MM.text"。
     - 如果logs文件夹不存在，则会自动创建。
    :return:
    """
    project_root = Path(__file__).resolve().parent.parent
    logs_dir = project_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{datetime.now():%Y-%m-%d_%H-%M}.text"
    return str(logs_dir / filename)


def setup_logging():
    """
    配置日志记录器，设置日志格式，并添加控制台和文件处理器
    """
    # 修改：使用 ColoredFormatter 替代 logging.Formatter
    formatter = ColoredFormatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    #文件名称根据日期自动生成
    file_handler = logging.FileHandler(get_daily_log_file_path(), encoding="utf-8")
    file_handler.setFormatter(formatter)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[console_handler, file_handler],
        force=True,
    )