# ==============================================================================
# Critical Note: This code was generated/modified by Gemini 3.1 Pro (High) access.
# ==============================================================================

import customtkinter as ctk
from tkinter import filedialog
from utils.config import save_config
from utils.logger import logger

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, master, current_config, on_save_callback, encoder_display_text=""):
        """
        系統進階設定面板
        """
        super().__init__(master)
        self.title("設定中心")
        self.geometry("400x350")
        self.resizable(False, False)
        # 設定為模態視窗 (Modal)
        self.transient(master)
        self.grab_set()
        
        self.current_config = current_config.copy()
        self.on_save_callback = on_save_callback
        self.encoder_display_text = encoder_display_text
        
        self.setup_ui()
        
    def setup_ui(self):
        # 標題
        ctk.CTkLabel(self, text="進階錄影設定", font=("Arial", 18, "bold")).pack(pady=(15, 10))
        
        # FPS 設定
        fps_frame = ctk.CTkFrame(self, fg_color="transparent")
        fps_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(fps_frame, text="錄影影格率 (FPS):").pack(side="left")
        self.fps_var = ctk.StringVar(value=str(self.current_config.get("fps", 30)))
        fps_menu = ctk.CTkOptionMenu(fps_frame, values=["15", "30", "60"], variable=self.fps_var)
        fps_menu.pack(side="right")
        
        # 儲存格式設定
        fmt_frame = ctk.CTkFrame(self, fg_color="transparent")
        fmt_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(fmt_frame, text="錄影輸出格式:").pack(side="left")
        self.fmt_var = ctk.StringVar(value=self.current_config.get("output_format", ".mkv"))
        fmt_menu = ctk.CTkOptionMenu(fmt_frame, values=[".mkv", ".mp4"], variable=self.fmt_var)
        fmt_menu.pack(side="right")
        
        # 影像編碼器 (硬體加速)
        enc_frame = ctk.CTkFrame(self, fg_color="transparent")
        enc_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(enc_frame, text="影片編碼器 (硬體加速):").pack(side="left")
        self.enc_var = ctk.StringVar(value=self.current_config.get("encoder", "Auto"))
        enc_menu = ctk.CTkOptionMenu(
            enc_frame, 
            values=["Auto", "libx264", "h264_nvenc", "h264_amf", "h264_qsv"], 
            variable=self.enc_var,
            width=120
        )
        enc_menu.pack(side="right")
        
        if "Auto" in self.encoder_display_text:
            ctk.CTkLabel(
                self, 
                text=f"*{self.encoder_display_text}*", 
                text_color="#17a2b8", font=("Arial", 11)
            ).pack(padx=20, anchor="w", pady=(0, 5))
        
        # 防當機說明
        ctk.CTkLabel(
            self, 
            text="* 使用非 CPU 編碼器前，請確定您的顯示卡支援該晶片。", 
            text_color="gray", font=("Arial", 10)
        ).pack(padx=20, anchor="w")
        
        # 儲存路徑
        path_frame = ctk.CTkFrame(self, fg_color="transparent")
        path_frame.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(path_frame, text="儲存資料夾:").pack(anchor="w")
        
        path_input_frame = ctk.CTkFrame(path_frame, fg_color="transparent")
        path_input_frame.pack(fill="x")
        self.path_var = ctk.StringVar(value=self.current_config.get("save_dir", "./Records"))
        self.path_entry = ctk.CTkEntry(path_input_frame, textvariable=self.path_var, state="disabled")
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(path_input_frame, text="瀏覽...", width=60, command=self.browse_folder)
        browse_btn.pack(side="right")
        
        # 儲存與取消
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(side="bottom", pady=20)
        
        ctk.CTkButton(btn_frame, text="儲存", fg_color="#28a745", hover_color="#218838", command=self.save_settings).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="取消", fg_color="gray", command=self.destroy).pack(side="left", padx=10)

    def browse_folder(self):
        # 必須透過 after() 在主執行緒開啟檔案視窗，否則會導致 CTkToplevel 當機
        self.grab_release()
        folder = filedialog.askdirectory(parent=self, title="選擇錄影儲存資料夾")
        self.grab_set()
        if folder:
            self.path_var.set(folder)
            
    def save_settings(self):
        self.current_config["fps"] = int(self.fps_var.get())
        self.current_config["output_format"] = self.fmt_var.get()
        self.current_config["save_dir"] = self.path_var.get()
        self.current_config["encoder"] = self.enc_var.get()
        
        # 寫入檔案
        save_config(self.current_config)
        logger.info(f"設定已更新: {self.current_config}")
        
        # 回調更新主程式狀態
        self.on_save_callback(self.current_config)
        self.destroy()
