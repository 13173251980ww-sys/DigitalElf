from pathlib import Path
from typing import Any, Dict
import yaml
from flask.cli import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"

# 全局配置变量
GLOBAL_CONFIG: Dict[str, Any] = {}

#加载环境变量
load_dotenv()

def _read_config_file() -> Dict[str, Any]:
	with CONFIG_PATH.open("r", encoding="utf-8") as f:
		data = yaml.safe_load(f) or {}

	return data


def reload_config() -> Dict[str, Any]:
	"""读取config.yaml并存到全局变量"""
	global GLOBAL_CONFIG
	GLOBAL_CONFIG = _read_config_file()

	return GLOBAL_CONFIG


def get_config() -> Dict[str, Any]:
	"""获取全局配置，如果尚未加载则先加载"""
	if not GLOBAL_CONFIG:
		reload_config()
	return GLOBAL_CONFIG


#在加载时先读取一次配置
reload_config()

