; MeetFlow 安裝檔編譯腳本 (Inno Setup)
; Software Design by RYAN LEE © 2026

[Setup]
; 應用程式基本資訊
AppName=MeetFlow Screen Recorder
AppVersion=1.0
AppPublisher=RYAN LEE
AppCopyright=Copyright (C) 2026 RYAN LEE. All rights reserved.
; 預設安裝路徑
DefaultDirName={autopf}\MeetFlow
; 開始選單資料夾名稱
DefaultGroupName=MeetFlow
; 輸出的安裝檔名稱與位置
OutputDir=Output
OutputBaseFilename=MeetFlow_Setup_v1.0
; 壓縮方式 (高壓縮比)
Compression=lzma2/ultra64
SolidCompression=yes
; 需要管理員權限進行安裝
PrivilegesRequired=admin
; 允許解除安裝
Uninstallable=yes

[Tasks]
; 讓使用者選擇是否建立桌面捷徑
Name: "desktopicon"; Description: "建立桌面捷徑"; GroupDescription: "附加選項:"; Flags: unchecked

[Files]
; 複製打包出來的整個資料夾內容到安裝目錄
Source: "dist\MeetFlow\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; 建立開始選單捷徑
Name: "{group}\MeetFlow"; Filename: "{app}\MeetFlow.exe"
; 建立解除安裝捷徑
Name: "{group}\解除安裝 MeetFlow"; Filename: "{uninstallexe}"
; 建立桌面捷徑
Name: "{autodesktop}\MeetFlow"; Filename: "{app}\MeetFlow.exe"; Tasks: desktopicon

[Run]
; 安裝完成後提供執行選項
Filename: "{app}\MeetFlow.exe"; Description: "啟動 MeetFlow"; Flags: nowait postinstall skipifsilent
