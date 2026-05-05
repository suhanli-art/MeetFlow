# ==============================================================================
# Critical Note: This code was generated/modified by Gemini 3.1 Pro (High) access.
# ==============================================================================

import customtkinter as ctk
import threading
import os
import keyboard
from ui.region_selector import RegionSelector
from ui.floating_widget import FloatingWidget
from ui.settings_window import SettingsWindow
from ui.remux_window import RemuxWindow
from core.video_capture import VideoCaptureEngine
from core.audio_capture import AudioCaptureEngine
from core.muxer import MuxerEngine
from utils.config import load_config
from utils.logger import logger

class AppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MeetFlow v1.0.3-beta")
        self.geometry("450x540")
        self.resizable(False, False)
        
        # 載入設定
        self.config = load_config()
        
        # 決定真實的編碼器
        configured_enc = self.config.get("encoder", "Auto")
        if configured_enc == "Auto":
            from utils.hardware_detector import detect_best_encoder
            import imageio_ffmpeg
            self.active_encoder = detect_best_encoder(imageio_ffmpeg.get_ffmpeg_exe())
            self.encoder_display_text = f"自動偵測 ({self.active_encoder})"
        else:
            self.active_encoder = configured_enc
            self.encoder_display_text = configured_enc
        
        # 狀態變數
        self.is_recording = False
        self.capture_region = None  # None 代表全螢幕
        self.floating_widget = None
        
        # 引擎模組初始化
        self.video_engine = VideoCaptureEngine(
            fps=self.config.get("fps", 30), 
            encoder=self.active_encoder
        )
        self.audio_engine = AudioCaptureEngine(sample_rate=48000)
        self.muxer_engine = MuxerEngine()
        
        # 執行緒與同步鎖
        self.start_event = threading.Event()
        self.stop_event = threading.Event()
        self.threads = []
        
        # 暫存檔強制使用 .mkv 以防止壞檔
        self.temp_video = "temp_video.mkv"
        self.temp_sys_audio = "temp_sys_audio.wav"
        self.temp_mic_audio = "temp_mic_audio.wav"
        
        self.setup_ui()
        
        # 註冊全域快捷鍵
        try:
            keyboard.add_hotkey('ctrl+shift+r', self.on_hotkey_pressed)
            logger.info("全域快捷鍵 Ctrl+Shift+R 已註冊。")
        except Exception as e:
            logger.warning(f"全域快捷鍵註冊失敗: {e}")
            
    def on_hotkey_pressed(self):
        self.after(0, self.toggle_recording)
        
    def setup_ui(self):
        # 頂部工具列
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        ctk.CTkButton(top_frame, text="⚙️ 設定", width=60, fg_color="gray", command=self.open_settings).pack(side="right", padx=5)
        ctk.CTkButton(top_frame, text="🔄 MKV 轉檔", width=80, fg_color="#17a2b8", command=self.open_remux).pack(side="right", padx=5)
        
        # 狀態區
        self.status_label = ctk.CTkLabel(
            self, text="● 準備就緒", text_color="gray", font=("Arial", 18, "bold")
        )
        self.status_label.pack(pady=(10, 0))
        
        # 顯示目前掛載的引擎
        self.engine_label = ctk.CTkLabel(
            self, text=f"掛載引擎: {self.encoder_display_text}", text_color="#17a2b8", font=("Arial", 10)
        )
        self.engine_label.pack(pady=(0, 5))
        
        # 區域與檔名區塊
        info_frame = ctk.CTkFrame(self)
        info_frame.pack(fill="x", padx=20, pady=5)
        
        self.region_label = ctk.CTkLabel(info_frame, text="錄影區域：全螢幕", font=("Arial", 12))
        self.region_label.pack(pady=(5, 0))
        self.region_btn = ctk.CTkButton(
            info_frame, text="選取錄影區域", command=self.open_region_selector,
            fg_color="#007bff", hover_color="#0056b3", height=25
        )
        self.region_btn.pack(pady=(5, 10))
        
        name_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        name_frame.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkLabel(name_frame, text="檔案名稱:").pack(side="left")
        self.filename_var = ctk.StringVar(value="MeetFlow_Record")
        self.filename_entry = ctk.CTkEntry(name_frame, textvariable=self.filename_var)
        self.filename_entry.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # 雙音軌設定區塊
        audio_frame = ctk.CTkFrame(self)
        audio_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(audio_frame, text="錄音設定", font=("Arial", 14, "bold")).pack(pady=(5, 0))
        
        sys_frame = ctk.CTkFrame(audio_frame, fg_color="transparent")
        sys_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(sys_frame, text="系統音 (課程)").pack(side="left")
        self.sys_slider = ctk.CTkSlider(sys_frame, from_=0, to=2.0, number_of_steps=20)
        self.sys_slider.set(1.0)
        self.sys_slider.pack(side="right", fill="x", expand=True, padx=10)
        
        mic_frame = ctk.CTkFrame(audio_frame, fg_color="transparent")
        mic_frame.pack(fill="x", padx=10, pady=5)
        self.mic_checkbox = ctk.CTkCheckBox(mic_frame, text="麥克風 (解說)", onvalue=True, offvalue=False)
        self.mic_checkbox.select()
        self.mic_checkbox.pack(side="left")
        self.mic_slider = ctk.CTkSlider(mic_frame, from_=0, to=2.0, number_of_steps=20)
        self.mic_slider.set(1.0)
        self.mic_slider.pack(side="right", fill="x", expand=True, padx=10)
        
        # 錄影控制區
        self.record_button = ctk.CTkButton(
            self, text="開始錄影 (Ctrl+Shift+R)", command=self.toggle_recording,
            fg_color="#28a745", hover_color="#218838",
            font=("Arial", 14, "bold"), height=50, width=200
        )
        self.record_button.pack(pady=(15, 5))
        
        # 版權宣告
        ctk.CTkLabel(
            self, text="Software Design by RYAN LEE © 2026 All Rights Reserved.", 
            text_color="gray", font=("Arial", 9)
        ).pack(side="bottom", pady=(0, 5))

    def open_settings(self):
        SettingsWindow(self, self.config, self.on_config_saved, self.encoder_display_text)
        
    def open_remux(self):
        RemuxWindow(self)

    def on_config_saved(self, new_config):
        self.config = new_config
        # 更新影像引擎的 FPS
        self.video_engine.fps = self.config.get("fps", 30)
        self.video_engine.frame_duration = 1.0 / self.video_engine.fps
        
        # 重新決定編碼器
        configured_enc = self.config.get("encoder", "Auto")
        if configured_enc == "Auto":
            from utils.hardware_detector import detect_best_encoder
            import imageio_ffmpeg
            self.active_encoder = detect_best_encoder(imageio_ffmpeg.get_ffmpeg_exe())
            self.encoder_display_text = f"自動偵測 ({self.active_encoder})"
        else:
            self.active_encoder = configured_enc
            self.encoder_display_text = configured_enc
            
        self.video_engine.encoder = self.active_encoder
        self.engine_label.configure(text=f"掛載引擎: {self.encoder_display_text}")

    def open_region_selector(self):
        self.withdraw()
        RegionSelector(self, self.on_region_selected)
        
    def on_region_selected(self, region):
        self.deiconify()
        if region:
            self.capture_region = region
            self.region_label.configure(text=f"錄影區域：{region['width']}x{region['height']}")
        else:
            self.capture_region = None
            self.region_label.configure(text="錄影區域：全螢幕")

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.is_recording = True
        self.stop_event.clear()
        self.start_event.clear()
        self.threads.clear()
        
        self.record_button.configure(text="停止錄影 (Ctrl+Shift+R)", fg_color="#dc3545", hover_color="#c82333")
        self.status_label.configure(text="● 錄影中...", text_color="#dc3545")
        self.region_btn.configure(state="disabled")
        
        self.iconify()
        self.floating_widget = FloatingWidget(self, self.stop_recording)
        
        for tmp in [self.temp_video, self.temp_sys_audio, self.temp_mic_audio]:
            if os.path.exists(tmp):
                try: os.remove(tmp)
                except: pass
                
        t_video = threading.Thread(
            target=self.video_engine.record_video, 
            args=(self.start_event, self.stop_event, self.capture_region, self.temp_video), 
            daemon=True
        )
        self.threads.append(t_video)
        
        t_sys = threading.Thread(
            target=self.audio_engine.record_audio,
            args=('system', self.temp_sys_audio, self.start_event, self.stop_event),
            daemon=True
        )
        t_keep = threading.Thread(
            target=self.audio_engine.keep_wasapi_alive,
            args=(self.start_event, self.stop_event),
            daemon=True
        )
        self.threads.extend([t_sys, t_keep])
        
        if self.mic_checkbox.get():
            t_mic = threading.Thread(
                target=self.audio_engine.record_audio,
                args=('mic', self.temp_mic_audio, self.start_event, self.stop_event),
                daemon=True
            )
            self.threads.append(t_mic)
            
        for t in self.threads:
            t.start()
            
        self.start_event.set()

    def stop_recording(self):
        if not self.is_recording: return
        self.is_recording = False
        
        if self.floating_widget:
            self.floating_widget.on_close()
            self.floating_widget = None
        self.deiconify()
        
        self.record_button.configure(text="處理中...", state="disabled", fg_color="gray")
        self.status_label.configure(text="● 正在合成影音...", text_color="#fd7e14")
        
        self.stop_event.set()
        threading.Thread(target=self.finalize_recording, daemon=True).start()
        
    def finalize_recording(self):
        for t in self.threads:
            t.join()
            
        sys_vol = self.sys_slider.get()
        mic_vol = self.mic_slider.get() if self.mic_checkbox.get() else 0
        custom_name = self.filename_var.get()
        
        success = self.muxer_engine.mix_and_mux(
            self.temp_video, self.temp_sys_audio, self.temp_mic_audio,
            save_dir=self.config.get("save_dir", "./Records"),
            custom_name=custom_name,
            output_format=self.config.get("output_format", ".mkv"),
            sys_volume=sys_vol, mic_volume=mic_vol
        )
        
        self.after(0, lambda: self.reset_ui(success))
        
    def reset_ui(self, success):
        self.record_button.configure(text="開始錄影 (Ctrl+Shift+R)", state="normal", fg_color="#28a745", hover_color="#218838")
        self.region_btn.configure(state="normal")
        if success:
            self.status_label.configure(text="● 錄影完成！已儲存。", text_color="#17a2b8")
        else:
            self.status_label.configure(text="● 錄影失敗，請查看日誌。", text_color="red")
