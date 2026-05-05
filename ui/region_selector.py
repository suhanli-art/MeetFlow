# ==============================================================================
# Critical Note: This code was generated/modified by Gemini 3.1 Pro (High) access.
# ==============================================================================

import tkinter as tk

class RegionSelector(tk.Toplevel):
    def __init__(self, parent, callback):
        """
        全螢幕區域選取遮罩
        callback: 當選取完成時，呼叫 callback(region_dict) 回傳座標
        """
        super().__init__(parent)
        self.callback = callback
        
        # 隱藏標題列，設定全螢幕與半透明
        self.overrideredirect(True)
        self.attributes('-alpha', 0.4)
        self.configure(bg='black')
        self.attributes("-topmost", True)
        
        # 獲取全螢幕尺寸 (含多螢幕)
        # 若需要跨螢幕選取，可以簡單使用 winfo_screenwidth()
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+0+0")
        
        # 畫布用來繪製選取框
        self.canvas = tk.Canvas(self, cursor="cross", bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # 變數
        self.start_x = None
        self.start_y = None
        self.rect = None
        
        # 綁定滑鼠事件
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        # 按下 Esc 或右鍵取消
        self.bind("<Escape>", self.cancel)
        self.canvas.bind("<ButtonPress-3>", self.cancel)

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        # 建立紅色矩形框
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='red', width=3)

    def on_move_press(self, event):
        curX, curY = (event.x, event.y)
        # 更新矩形大小
        self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)

    def on_button_release(self, event):
        end_x = event.x
        end_y = event.y
        
        # 計算左上角與長寬
        left = min(self.start_x, end_x)
        top = min(self.start_y, end_y)
        width = abs(self.start_x - end_x)
        height = abs(self.start_y - end_y)
        
        # 如果選取範圍太小，當作取消
        if width < 10 or height < 10:
            self.cancel()
            return
            
        # H.264 要求長寬必須是偶數
        if width % 2 != 0: width -= 1
        if height % 2 != 0: height -= 1
            
        region = {
            "top": top,
            "left": left,
            "width": width,
            "height": height
        }
        
        self.destroy()
        self.callback(region)
        
    def cancel(self, event=None):
        self.destroy()
        self.callback(None)
