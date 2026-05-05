# ==============================================================================
# Critical Note: This code was generated/modified by Gemini 3.1 Pro (High) access.
# ==============================================================================

import subprocess
import os
import imageio_ffmpeg
from datetime import datetime
from utils.logger import logger

class MuxerEngine:
    def __init__(self):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    def mix_and_mux(self, temp_video, temp_sys_audio, temp_mic_audio, save_dir, custom_name, output_format, sys_volume=1.0, mic_volume=1.0):
        """
        將獨立錄製的影像與雙音軌合成為最終檔案。
        支援自訂檔名前綴與輸出格式 (.mkv 或 .mp4)。
        """
        if not os.path.exists(save_dir):
            try: os.makedirs(save_dir)
            except Exception as e: logger.error(f"建立資料夾失敗: {e}")

        # 產生輸出檔名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = custom_name.strip() if custom_name and custom_name.strip() else "Record"
        filename = f"{prefix}_{timestamp}{output_format}"
        output_filepath = os.path.join(save_dir, filename)
            
        if not os.path.exists(temp_video):
            logger.error("混流失敗：找不到暫存影像檔。")
            return False

        has_sys = os.path.exists(temp_sys_audio)
        has_mic = os.path.exists(temp_mic_audio)

        mux_cmd = [self.ffmpeg_exe, '-y', '-i', temp_video]
        
        # 根據存在的音訊檔案動態構建 FFmpeg 指令
        if has_sys and has_mic:
            mux_cmd.extend(['-i', temp_sys_audio, '-i', temp_mic_audio])
            filter_str = (
                f"[1:a]volume={sys_volume}[a1];"
                f"[2:a]volume={mic_volume}[a2];"
                f"[a1][a2]amix=inputs=2:duration=longest[a]"
            )
            mux_cmd.extend([
                '-filter_complex', filter_str,
                '-map', '0:v', '-map', '[a]',
                '-c:v', 'copy', '-c:a', 'aac',
                output_filepath
            ])
        elif has_sys:
            mux_cmd.extend(['-i', temp_sys_audio])
            mux_cmd.extend([
                '-filter_complex', f"[1:a]volume={sys_volume}[a]",
                '-map', '0:v', '-map', '[a]',
                '-c:v', 'copy', '-c:a', 'aac',
                output_filepath
            ])
        elif has_mic:
            mux_cmd.extend(['-i', temp_mic_audio])
            mux_cmd.extend([
                '-filter_complex', f"[1:a]volume={mic_volume}[a]",
                '-map', '0:v', '-map', '[a]',
                '-c:v', 'copy', '-c:a', 'aac',
                output_filepath
            ])
        else:
            mux_cmd.extend(['-c:v', 'copy', output_filepath])

        logger.info(f"開始執行 FFmpeg 混流，輸出路徑: {output_filepath}")
        
        try:
            subprocess.run(mux_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            logger.info(f"影音合成完畢，已儲存為 {output_filepath}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg 混流過程中發生錯誤: {e}")
            return False
        finally:
            # 確保清理暫存檔
            for tmp in [temp_video, temp_sys_audio, temp_mic_audio]:
                if os.path.exists(tmp):
                    try: os.remove(tmp)
                    except Exception as e: logger.warning(f"無法刪除暫存檔 {tmp}: {e}")
