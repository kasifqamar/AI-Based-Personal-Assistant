import requests
from typing import Dict, Optional
from config import APIConfig
from modules.json_db import db

class WeatherModule:
    def __init__(self):
        self.api_key = APIConfig.OPENWEATHER_API_KEY
        self.base_url = APIConfig.OPENWEATHER_BASE_URL

    def get_current_weather(self, location: str = None) -> Dict:
        if not location:
            prefs = db.get_user_preferences()
            loc = prefs.get('location', {})
            location = f"{loc.get('city', 'New York')},{loc.get('country', 'US')}"
        params = {'q': location, 'appid': self.api_key, 'units': 'metric'}
        try:
            resp = requests.get(APIConfig.CURRENT_WEATHER_URL, params=params)
            resp.raise_for_status()
            return resp.json()
        except:
            return {}

    def get_weather_forecast(self, location: str = None) -> Dict:
        if not location:
            prefs = db.get_user_preferences()
            loc = prefs.get('location', {})
            location = f"{loc.get('city', 'New York')},{loc.get('country', 'US')}"
        params = {'q': location, 'appid': self.api_key, 'units': 'metric', 'cnt': 8}
        try:
            resp = requests.get(APIConfig.FORECAST_URL, params=params)
            resp.raise_for_status()
            return resp.json()
        except:
            return {}
