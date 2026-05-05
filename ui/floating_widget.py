# ==============================================================================
# Critical Note: This code was generated/modified by Gemini 3.1 Pro (High) access.
# ==============================================================================

import customtkinter as ctk
import time

class FloatingWidget(ctk.CTkToplevel):
    def __init__(self, master, stop_callback):
        """
        全域置頂浮動控制台
        master: AppWindow (主視窗)
        stop_callback: 當點擊停止按鈕時的處理函式
        """
        super().__init__(master)
        self.stop_callback = stop_callback
        
        # 移除系統邊框，永遠置頂
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color="#1e1e1e")
        
        # 隱藏原本的預設行為
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # 狀態變數
        self.start_time = time.perf_counter()
        self.is_running = True
        self.dot_visible = True
        
        self.setup_ui()
        self.position_widget()
        self.update_timer()
        
    def setup_ui(self):
        # 紅色閃爍錄影點
        self.dot_label = ctk.CTkLabel(self, text="●", text_color="red", font=("Arial", 20, "bold"))
        self.dot_label.pack(side="left", padx=(10, 5), pady=5)
        
        # 時間顯示
        self.time_label = ctk.CTkLabel(self, text="00:00:00", text_color="white", font=("Courier", 16, "bold"))
        self.time_label.pack(side="left", padx=5, pady=5)
        
        # 停止按鈕 (方形小圖示)
        self.stop_btn = ctk.CTkButton(
            self, text="⏹", width=30, height=30,
            fg_color="#dc3545", hover_color="#c82333",
            font=("Arial", 16), command=self.on_stop_click
        )
        self.stop_btn.pack(side="right", padx=(10, 10), pady=5)

    def position_widget(self):
        # 放置在右下角
        # 固定寬高
        w = 160
        h = 50
        # 獲取螢幕尺寸
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        # 留邊距 30px
        x = screen_w - w - 30
        y = screen_h - h - 60  # 避開工作列
        
        self.geometry(f"{w}x{h}+{x}+{y}")
        
    def update_timer(self):
        if not self.is_running:
            return
            
        # 計算經過時間
        elapsed = int(time.perf_counter() - self.start_time)
        hrs = elapsed // 3600
        mins = (elapsed % 3600) // 60
        secs = elapsed % 60
        time_str = f"{hrs:02d}:{mins:02d}:{secs:02d}"
        
        self.time_label.configure(text=time_str)
        
        # 紅點閃爍邏輯
        self.dot_visible = not self.dot_visible
        self.dot_label.configure(text_color="red" if self.dot_visible else "#1e1e1e")
        
        # 每 500 毫秒更新一次
        self.after(500, self.update_timer)
        
    def on_stop_click(self):
        self.is_running = False
        self.time_label.configure(text="處理中...")
        self.dot_label.configure(text_color="gray")
        self.stop_btn.configure(state="disabled")
        # 呼叫主視窗的停止邏輯
        self.stop_callback()
        
    def on_close(self):
        self.is_running = False
        self.destroy()
