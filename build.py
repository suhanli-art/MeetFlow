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
