# ==============================================================================
# Critical Note: This code was generated/modified by Gemini 3.1 Pro (High) access.
# ==============================================================================

import subprocess
import os
import tempfile
from utils.logger import logger

def detect_best_encoder(ffmpeg_exe):
    """
    智慧硬體探測演算法 (Hardware Probing Algorithm)
    透過在背景產生極短的測試片段，依序測試各大廠牌的硬體加速晶片。
    """
    logger.info("開始執行硬體加速晶片自動探測...")
    
    # 按照優先度排序：NVIDIA -> Intel -> AMD
    encoders_to_test = ['h264_nvenc', 'h264_qsv', 'h264_amf']
    
    # 建立一個隱藏的暫存路徑供測試輸出
    test_out = os.path.join(tempfile.gettempdir(), 'meetflow_probe_test.mkv')
    
    for enc in encoders_to_test:
        # 指令邏輯：產生 0.1 秒的全黑畫面，嘗試使用指定的 encoder 進行轉檔
        # -f lavfi -i color=c=black:s=128x128:r=30 -t 0.1
        cmd = [
            ffmpeg_exe, '-y',
            '-f', 'lavfi', '-i', 'color=c=black:s=128x128:r=30',
            '-c:v', enc,
            '-t', '0.1',
            test_out
        ]
        
        try:
            # 必須捕捉錯誤，且設定 timeout 避免卡死
            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
            if res.returncode == 0:
                logger.info(f"自動偵測成功！已鎖定硬體加速晶片: {enc}")
                try: os.remove(test_out)
                except: pass
                return enc
        except Exception:
            pass
            
    # 如果所有硬體測試都失敗，退回最穩定的 CPU 編碼
    logger.warning("未偵測到相容的硬體加速晶片，將使用預設 CPU 編碼 (libx264)")
    try: os.remove(test_out)
    except: pass
    return 'libx264'
