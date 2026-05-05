# ==============================================================================
# Critical Note: This code was generated/modified by Gemini 3.1 Pro (High) access.
# ==============================================================================

import soundcard as sc
import soundfile as sf
import numpy as np
import time
import threading
from utils.logger import logger

class AudioCaptureEngine:
    def __init__(self, sample_rate=48000):
        self.sample_rate = sample_rate

    def keep_wasapi_alive(self, start_event, stop_event):
        """背景靜音播放器，確保 WASAPI Loopback 在系統靜音時不會中斷串流"""
        try:
            default_speaker = sc.default_speaker()
            with default_speaker.player(samplerate=self.sample_rate) as sp:
                silence = np.zeros((4800, 2), dtype=np.float32)
                start_event.wait()
                while not stop_event.is_set():
                    sp.play(silence)
        except Exception as e:
            logger.debug(f"Keep-alive 執行緒無法啟動 (可忽略): {e}")

    def record_audio(self, device_type, output_file, start_event, stop_event):
        """
        通用的音訊錄製邏輯，支援系統音效 (loopback) 或麥克風。
        device_type: 'system' 或 'mic'
        """
        mic = None
        try:
            if device_type == 'system':
                default_speaker = sc.default_speaker()
                mic = sc.get_microphone(default_speaker.id, include_loopback=True)
                logger.info(f"成功連線至系統音效迴圈: {default_speaker.name}")
            else:
                mic = sc.default_microphone()
                logger.info(f"成功連線至麥克風: {mic.name}")
        except Exception as e:
            logger.warning(f"無法存取 {device_type} 裝置: {e}。此音軌將留空。")
            return

        try:
            with mic.recorder(samplerate=self.sample_rate) as recorder:
                initial_data = recorder.record(numframes=10)
                channels = initial_data.shape[1]
                
                with sf.SoundFile(output_file, mode='w', samplerate=self.sample_rate, channels=channels) as file:
                    file.write(initial_data)
                    
                    start_event.wait()
                    start_time = time.perf_counter()
                    total_frames_written = 0
                    
                    while not stop_event.is_set():
                        data = recorder.record(numframes=1024)
                        frames_read = len(data)
                        
                        file.write(data)
                        total_frames_written += frames_read
                        
                        # 動態靜音補償 (Silence Padding)
                        now = time.perf_counter()
                        elapsed = now - start_time
                        expected_frames = int(elapsed * self.sample_rate)
                        
                        missing_frames = expected_frames - total_frames_written
                        # 容忍約 50ms 的落差
                        if missing_frames > 2400:
                            silence_data = np.zeros((missing_frames, channels), dtype=np.float32)
                            file.write(silence_data)
                            total_frames_written += missing_frames
                            logger.debug(f"[{device_type}] 觸發斷流防護，自動補齊 {missing_frames} frames 靜音。")
                            
            logger.info(f"{device_type} 錄製結束。")
        except Exception as e:
            logger.error(f"{device_type} 錄音執行緒發生錯誤: {e}", exc_info=True)
