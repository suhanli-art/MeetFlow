import PyInstaller.__main__
import os

# 確認我們在正確的目錄
current_dir = os.path.dirname(os.path.abspath(__file__))
main_script = os.path.join(current_dir, "main.py")

print("==================================================")
print("  Building MeetFlow Commercial Edition (by RYAN LEE)")
print("==================================================")

PyInstaller.__main__.run([
    main_script,
    '--name=MeetFlow',
    '--onedir',          # 打包為資料夾，啟動速度最快
    '--windowed',        # 隱藏終端機視窗
    '--collect-all=imageio_ffmpeg', # 強制包入 ffmpeg.exe (解決打包後找不到 FFmpeg 的問題)
    '--collect-all=mss',            # 強制包入 mss 擷取模組 (解決 module has no attribute MSS)
    '--collect-all=soundcard',      # 強制包入 soundcard 音效模組
    '--hidden-import=imageio_ffmpeg',
    '--hidden-import=soundcard',
    '--hidden-import=soundfile',
    '--hidden-import=mss',
    '--hidden-import=customtkinter',
    '--hidden-import=keyboard',
    '--clean'
])

print("\n==================================================")
print("  Build completed! Executable is at dist/MeetFlow/MeetFlow.exe")
print("==================================================")
