import requests
from typing import List, Dict
from config import APIConfig, AssistantConfig
from modules.json_db import db

class NewsModule:
    def __init__(self):
        self.api_key = APIConfig.NEWS_API_KEY
        self.base_url = APIConfig.NEWS_API_URL

    def get_news(self, category=None, count=5):
        prefs = db.get_user_preferences().get('news_preferences', {})
        params = {
            'apiKey': self.api_key,
            'pageSize': count,
            'language': prefs.get('language', 'en')
        }
        if category:
            params['category'] = category
        elif prefs.get('categories'):
            params['category'] = prefs['categories'][0]
        if prefs.get('sources'):
            params['sources'] = ','.join(prefs['sources'])
        try:
            resp = requests.get(self.base_url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get('articles', [])
        except:
            return []
