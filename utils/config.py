# ==============================================================================
# Critical Note: This code was generated/modified by Gemini 3.1 Pro (High) access.
# ==============================================================================

import json
import os
from utils.logger import logger
from utils.paths import get_app_data_dir, get_default_records_dir

CONFIG_FILE = os.path.join(get_app_data_dir(), "config.json")

DEFAULT_CONFIG = {
    "fps": 30,
    "output_format": ".mkv",
    "save_dir": get_default_records_dir(),
    "encoder": "Auto"
}

def load_config():
    """從本機讀取設定檔，若無則建立預設設定檔"""
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
        
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            # 確保舊設定檔也有新欄位
            for k, v in DEFAULT_CONFIG.items():
                if k not in config:
                    config[k] = v
            return config
    except Exception as e:
        logger.error(f"讀取設定檔失敗，使用預設值: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config_dict):
    """儲存設定至本機"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=4, ensure_ascii=False)
        logger.info("設定檔儲存成功。")
    except Exception as e:
        logger.error(f"儲存設定檔失敗: {e}")
