import threading
import time
import re
import json
import os
import pyttsx3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import PathConfig
from PyQt5.QtCore import QObject, pyqtSignal
import dateparser

class ReminderModule(QObject):
    reminder_triggered = pyqtSignal(str, str)  # name, message

    def __init__(self):
        super().__init__()
        self.reminders: List[Dict] = []
        self.active_reminders: Dict[str, List[threading.Timer]] = {}  # name: [main_timer, pre_timer]
        self.speaker = pyttsx3.init()
        self.load_reminders()

    def speak(self, text: str):
        self.speaker.say(text)
        self.speaker.runAndWait()

    def add_reminder(self, name: str, message: str, trigger_time: datetime) -> bool:
        reminder = {
            'name': name,
            'message': message,
            'trigger_time': trigger_time.isoformat(),
            'created_at': datetime.now().isoformat()
        }

        if any(r['name'].lower() == name.lower() for r in self.reminders):
            return False  # Duplicate

        self.reminders.append(reminder)
        self.schedule_reminder(reminder)
        self.save_reminders()
        return True

    def schedule_reminder(self, reminder: Dict):
        try:
            name = reminder['name']
            message = reminder['message']
            trigger_time = datetime.fromisoformat(reminder['trigger_time'])
            now = datetime.now()

            if trigger_time <= now:
                print(f"Reminder '{name}' is in the past. Skipping...")
                return

            # Cancel existing timers
            if name in self.active_reminders:
                for t in self.active_reminders[name]:
                    t.cancel()

            delay_main = (trigger_time - now).total_seconds()
            delay_pre = delay_main - 600  # 10 minutes before

            timers = []

            if delay_pre > 0:
                t_pre = threading.Timer(delay_pre, self.trigger_pre_reminder, args=[name, message])
                t_pre.start()
                timers.append(t_pre)

            t_main = threading.Timer(delay_main, self.trigger_reminder, args=[reminder])
            t_main.start()
            timers.append(t_main)

            self.active_reminders[name] = timers
        except Exception as e:
            print(f"Error scheduling reminder: {e}")

    def trigger_pre_reminder(self, name: str, message: str):
        notice = f"Reminder: {message} in 10 minutes"
        print(notice)
        self.speak(notice)

    def trigger_reminder(self, reminder: Dict):
        name = reminder['name']
        message = reminder['message']
        print(f"Reminder now: {message}")
        self.speak(message)
        self.reminder_triggered.emit(name, message)
        self.remove_reminder(name)

    def remove_reminder(self, name: str) -> bool:
        if name in self.active_reminders:
            for t in self.active_reminders[name]:
                t.cancel()
            del self.active_reminders[name]

        before = len(self.reminders)
        self.reminders = [r for r in self.reminders if r['name'].lower() != name.lower()]
        if len(self.reminders) < before:
            self.save_reminders()
            return True
        return False

    def remove_all_reminders(self):
        for timers in self.active_reminders.values():
            for t in timers:
                t.cancel()
        self.active_reminders.clear()
        self.reminders.clear()
        self.save_reminders()
        self.speak("All reminders have been deleted.")
        print("All reminders deleted.")

    def get_reminders(self) -> List[Dict]:
        now = datetime.now()
        return [r for r in self.reminders if datetime.fromisoformat(r['trigger_time']) > now]

    def save_reminders(self):
        reminder_file = PathConfig.DATABASE_DIR / "reminders.json"
        try:
            os.makedirs(PathConfig.DATABASE_DIR, exist_ok=True)
            with open(reminder_file, 'w') as f:
                json.dump(self.reminders, f, indent=2)
        except Exception as e:
            print(f"Error saving reminders: {e}")

    def load_reminders(self):
        reminder_file = PathConfig.DATABASE_DIR / "reminders.json"
        try:
            if reminder_file.exists():
                with open(reminder_file, 'r') as f:
                    self.reminders = json.load(f)
                for r in self.reminders:
                    self.schedule_reminder(r)
        except Exception as e:
            print(f"Error loading reminders: {e}")

    def parse_reminder_time(self, time_str: str) -> Optional[datetime]:
        parsed = dateparser.parse(time_str, settings={"PREFER_DATES_FROM": "future"})
        return parsed

    def extract_reminder_info(self, command: str) -> tuple:
        command = command.lower()
        if "delete all reminders" in command:
            return "DELETE_ALL", "DELETE_ALL", "DELETE_ALL"

        patterns = [
            r"remind me to (.+?) (at|on|by|for|after|in) (.+)",
            r"set a? ?reminder (?:for|about) (.+?) (at|on|by|after|in) (.+)",
            r"(.+?) at (.+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, command)
            if match:
                message = match.group(1).strip()
                time_str = match.group(3) if len(match.groups()) >= 3 else match.group(2)
                name = message[:30] + "..." if len(message) > 30 else message
                return name, message, time_str.strip()
        return None, None, None
