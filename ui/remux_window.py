# ==============================================================================
# Critical Note: This code was generated/modified by Gemini 3.1 Pro (High) access.
# ==============================================================================

import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import os
import threading
import imageio_ffmpeg
from utils.logger import logger

class RemuxWindow(ctk.CTkToplevel):
    def __init__(self, master):
        """
        MKV 無損轉 MP4 工具
        """
        super().__init__(master)
        self.title("MKV 轉檔工具 (Remux)")
        self.geometry("450x250")
        self.resizable(False, False)
        # 獨立視窗，但不阻擋主視窗
        
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        self.input_file = None
        self.output_file = None
        
        self.setup_ui()
        
    def setup_ui(self):
        ctk.CTkLabel(self, text="將安全的 MKV 無損轉換為 MP4", font=("Arial", 16, "bold")).pack(pady=(15, 5))
        ctk.CTkLabel(self, text="此過程不會重新編碼，畫質不變且速度極快。", text_color="gray", font=("Arial", 12)).pack()
        
        # 選擇檔案
        file_frame = ctk.CTkFrame(self, fg_color="transparent")
        file_frame.pack(fill="x", padx=20, pady=20)
        
        self.file_label = ctk.CTkLabel(file_frame, text="尚未選擇檔案...", width=300, anchor="w", fg_color="#333", corner_radius=5)
        self.file_label.pack(side="left", padx=(0, 10))
        
        browse_btn = ctk.CTkButton(file_frame, text="選擇 MKV", width=80, command=self.browse_file)
        browse_btn.pack(side="right")
        
        # 轉檔按鈕
        self.convert_btn = ctk.CTkButton(
            self, text="開始轉檔", command=self.start_conversion,
            fg_color="#007bff", hover_color="#0056b3", state="disabled",
            height=40
        )
        self.convert_btn.pack(pady=10)
        
        self.status_label = ctk.CTkLabel(self, text="")
        self.status_label.pack()

    def browse_file(self):
        filepath = filedialog.askopenfilename(
            parent=self,
            title="選擇要轉換的 MKV 檔案",
            filetypes=[("MKV Video Files", "*.mkv")]
        )
        if filepath:
            self.input_file = filepath
            filename = os.path.basename(filepath)
            self.file_label.configure(text=f" {filename}")
            
            # 預設輸出檔名
            name, _ = os.path.splitext(filepath)
            self.output_file = f"{name}.mp4"
            self.convert_btn.configure(state="normal")
            self.status_label.configure(text="")

    def start_conversion(self):
        if not self.input_file or not self.output_file:
            return
            
        if os.path.exists(self.output_file):
            if not messagebox.askyesno("檔案已存在", "目標 MP4 檔案已存在，是否覆蓋？"):
                return
                
        self.convert_btn.configure(state="disabled", text="轉檔中...")
        self.status_label.configure(text="FFmpeg 處理中，請稍候...", text_color="#fd7e14")
        
        threading.Thread(target=self.run_ffmpeg, daemon=True).start()
        
    def run_ffmpeg(self):
        cmd = [
            self.ffmpeg_exe, '-y',
            '-i', self.input_file,
            '-c', 'copy',
            self.output_file
        ]
        
        try:
            logger.info(f"開始 MKV 轉檔: {self.input_file} -> {self.output_file}")
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            self.after(0, self.on_success)
        except Exception as e:
            logger.error(f"轉檔失敗: {e}")
            self.after(0, self.on_error)
            
    def on_success(self):
        self.status_label.configure(text="轉檔成功！已儲存至相同資料夾。", text_color="#28a745")
        self.convert_btn.configure(state="normal", text="開始轉檔")
        
    def on_error(self):
        self.status_label.configure(text="轉檔發生錯誤，請查看日誌。", text_color="red")
        self.convert_btn.configure(state="normal", text="開始轉檔")
