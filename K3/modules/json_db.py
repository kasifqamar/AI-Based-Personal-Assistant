import json
import threading
from datetime import datetime
from pathlib import Path
from config import PathConfig

class JSONDatabase:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.file_path = PathConfig.USER_DATA_FILE
        if not self.file_path.exists():
            self._create_default_db()
        self._load_data()

    def _create_default_db(self):
        default_data = {
            "user_preferences": {
                "name": "User",
                "location": {"city": "New York", "country": "US"},
                "news_preferences": {"categories": ["technology", "science"], "language": "en", "sources": []},
                "theme": "dark",
                "voice_enabled": True
            },
            "chat_history": [],
            "system_settings": {
                "default_apps": {"browser": "chrome", "music": "spotify", "editor": "notepad"}
            }
        }
        with open(self.file_path, 'w') as f:
            json.dump(default_data, f, indent=4)

    def _load_data(self):
        with open(self.file_path, 'r') as f:
            self.data = json.load(f)

    def save(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f, indent=4)

    def get_user_preferences(self):
        return self.data.get('user_preferences', {})

    def update_user_preferences(self, preferences):
        self.data['user_preferences'] = preferences
        self.save()

    def get_chat_history(self):
        return self.data.get('chat_history', [])

    def add_chat_message(self, sender, message):
        self.data['chat_history'].append({
            'sender': sender,
            'message': message,
            'timestamp': str(datetime.now())
        })
        self.save()

    def clear_chat_history(self):
        self.data['chat_history'] = []
        self.save()

    def get_system_settings(self):
        return self.data.get('system_settings', {})

    def update_system_settings(self, settings):
        self.data['system_settings'] = settings
        self.save()

db = JSONDatabase()
