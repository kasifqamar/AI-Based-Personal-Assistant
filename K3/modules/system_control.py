import os
import platform
import subprocess
import pyautogui
from typing import Optional

class SystemControl:
    def __init__(self):
        self.system_os = platform.system().lower()

    def open_application(self, app_name: str) -> bool:
        app_mapping = {
            'chrome': {'windows': 'chrome.exe', 'darwin': 'Google Chrome', 'Linux': 'google-chrome'},
            'spotify': {'windows': 'Spotify.exe', 'darwin': 'Spotify', 'Linux': 'spotify'},
            'notepad': {'windows': 'notepad.exe', 'darwin': 'TextEdit', 'Linux': 'gedit'}
        }
        if app_name.lower() in app_mapping:
            os_name = self.system_os
            app = app_mapping[app_name.lower()].get(os_name)
            try:
                if os_name == 'windows':
                    os.startfile(app)
                else:
                    subprocess.Popen(app, shell=True)
                return True
            except:
                return False
        return False

    def increase_volume(self, amount=10):
        if self.system_os == 'windows':
            for _ in range(amount // 2): pyautogui.press('volumeup')
        elif self.system_os == 'darwin':
            pyautogui.hotkey('option', 'up')
        else:
            subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', f'{amount}%+'])

    def decrease_volume(self, amount=10):
        if self.system_os == 'windows':
            for _ in range(amount // 2): pyautogui.press('volumedown')
        elif self.system_os == 'darwin':
            pyautogui.hotkey('option', 'down')
        else:
            subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', f'{amount}%-'])

    def mute_volume(self):
        if self.system_os == 'windows':
            pyautogui.press('volumemute')
        elif self.system_os == 'darwin':
            pyautogui.hotkey('option', 'shift', 'down')
        else:
            subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', 'mute'])

    def unmute_volume(self):
        if self.system_os == 'windows':
            pyautogui.press('volumemute')
        elif self.system_os == 'darwin':
            pyautogui.hotkey('option', 'shift', 'up')
        else:
            subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', 'unmute'])

    def play_media(self):
        pyautogui.press('playpause')

    def pause_media(self):
        pyautogui.press('playpause')

    def stop_media(self):
        pyautogui.press('stop')

    def shutdown(self, delay=0):
        if self.system_os == 'windows':
            os.system(f"shutdown /s /t {delay}")
        elif self.system_os == 'darwin':
            os.system(f"shutdown -h +{delay//60}")
        else:
            os.system(f"shutdown -h +{delay//60}")

    def restart(self, delay=0):
        if self.system_os == 'windows':
            os.system(f"shutdown /r /t {delay}")
        elif self.system_os == 'darwin':
            os.system("shutdown -r now")
        else:
            os.system("shutdown -r now")

    def sleep(self):
        if self.system_os == 'windows':
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        elif self.system_os == 'darwin':
            os.system("pmset sleepnow")
        else:
            os.system("systemctl suspend")
