# ==============================================================================
# Critical Note: This code was generated/modified by Gemini 3.1 Pro (High) access.
# ==============================================================================

import os

def get_app_data_dir():
    """
    取得符合 Windows 規範的應用程式資料儲存路徑。
    通常位於 C:\\Users\\<Username>\\AppData\\Roaming\\MeetFlow
    """
    app_data = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'MeetFlow')
    if not os.path.exists(app_data):
        try:
            os.makedirs(app_data, exist_ok=True)
        except Exception:
            pass
    return app_data

def get_default_records_dir():
    """
    取得符合 Windows 規範的預設影片儲存路徑。
    通常位於 C:\\Users\\<Username>\\Videos\\MeetFlow
    """
    user_profile = os.environ.get('USERPROFILE', os.path.expanduser('~'))
    records_dir = os.path.join(user_profile, 'Videos', 'MeetFlow')
    if not os.path.exists(records_dir):
        try:
            os.makedirs(records_dir, exist_ok=True)
        except Exception:
            pass
    return records_dir
