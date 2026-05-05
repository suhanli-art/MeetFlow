# ==============================================================================
# Critical Note: This code was generated/modified by Gemini 3.1 Pro (High) access.
# ==============================================================================

import logging
import os
from datetime import datetime
from utils.paths import get_app_data_dir

def setup_logger(name="MeetFlow"):
    """
    商業級日誌系統：
    將系統運作狀態、警告與例外錯誤寫入 logs 目錄下，同時印出至終端機。
    """
    # 確保 logs 目錄存在於 AppData，避免 Program Files 權限被拒
    log_dir = os.path.join(get_app_data_dir(), "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
        
    logger = logging.getLogger(name)
    
    # 防止重複添加 handler
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        # 格式化
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(module)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # File Handler (寫入檔案)
        today_str = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(log_dir, f"meetflow_{today_str}.log")
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Stream Handler (輸出到終端機)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        
    return logger

# 提供一個全域可用的 logger 實例
logger = setup_logger()
