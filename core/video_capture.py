# ==============================================================================
# Critical Note: This code was generated/modified by Gemini 3.1 Pro (High) access.
# ==============================================================================

import mss
import subprocess
import mss
import subprocess
import time
import imageio_ffmpeg
from utils.logger import logger

class VideoCaptureEngine:
    def __init__(self, fps=30, encoder="libx264"):
        self.fps = fps
        self.encoder = encoder
        self.frame_duration = 1.0 / fps
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    def record_video(self, start_event, stop_event, capture_region, output_temp_file):
        """
        獨立的影像擷取迴圈。
        使用 mss 抓取指定區域，並透過 Frame Duplication 演算法保證恆定幀率 (CFR)。
        """
        try:
            with mss.MSS() as sct:
                # 若未指定區域，則預設為主螢幕
                if not capture_region:
                    monitor = sct.monitors[1]
                    width = monitor["width"]
                    height = monitor["height"]
                    if width % 2 != 0: width -= 1
                    if height % 2 != 0: height -= 1
                    capture_region = {
                        "top": monitor["top"],
                        "left": monitor["left"],
                        "width": width,
                        "height": height
                    }
                else:
                    width = capture_region["width"]
                    height = capture_region["height"]
                    
                logger.info(f"開始影像擷取，解析度: {width}x{height}，使用編碼器: {self.encoder}")
                
                # 建立 FFmpeg pipe
                ffmpeg_cmd = [
                    self.ffmpeg_exe,
                    '-y',
                    '-f', 'rawvideo',
                    '-vcodec', 'rawvideo',
                    '-pix_fmt', 'bgra',
                    '-s', f'{width}x{height}',
                    '-r', str(self.fps),
                    '-i', '-',
                    '-c:v', self.encoder,
                    '-preset', 'fast' if self.encoder != 'libx264' else 'ultrafast',
                    '-pix_fmt', 'yuv420p',
                    output_temp_file
                ]
                
                process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                
                # 等待同步起跑信號
                start_event.wait()
                
                start_time = time.perf_counter()
                next_frame_time = start_time
                frames_grabbed = 0
                frames_written = 0
                
                while not stop_event.is_set():
                    img = sct.grab(capture_region)
                    frame_bytes = img.bgra
                    frames_grabbed += 1
                    
                    # 寫入當前畫面
                    try:
                        process.stdin.write(frame_bytes)
                        frames_written += 1
                    except Exception as e:
                        logger.error(f"寫入影像資料至 FFmpeg 發生錯誤: {e}")
                        break
                        
                    next_frame_time += self.frame_duration
                    now = time.perf_counter()
                    
                    # 同步補償機制 (掉幀填補 / Frame Duplication)
                    if now < next_frame_time:
                        time.sleep(next_frame_time - now)
                    else:
                        duplicated = 0
                        while next_frame_time < now:
                            try:
                                process.stdin.write(frame_bytes)
                                frames_written += 1
                                duplicated += 1
                            except Exception:
                                break
                            next_frame_time += self.frame_duration
                        if duplicated > 0:
                            logger.debug(f"觸發影像補幀機制，複製了 {duplicated} 幀。")
                            
                try:
                    process.stdin.close()
                    process.wait()
                except Exception:
                    pass
                    
                logger.info(f"影像擷取結束。共抓取 {frames_grabbed} 幀，寫入 {frames_written} 幀。")
                
        except Exception as e:
            logger.error(f"影像錄製執行緒發生例外錯誤: {e}", exc_info=True)
