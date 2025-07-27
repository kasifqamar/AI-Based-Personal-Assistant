import httpx
from typing import Dict, Any
from config import APIConfig
from modules.json_db import db

class ChatModule:
    def __init__(self):
        self.api_key = APIConfig.GROQ_API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama3-70b-8192"  # Current Groq model

    def get_response(self, message: str) -> str:
        """Get formatted response text"""
        try:
            response = self._get_api_response(message)
            return response['choices'][0]['message']['content']
        except Exception as e:
            return f"Error processing response: {str(e)}"

    def get_response_raw(self, message: str) -> Dict[str, Any]:
        """Get raw API response (added to match expected interface)"""
        return self._get_api_response(message)

    def _get_api_response(self, message: str) -> Dict[str, Any]:
        """Internal method to handle API requests"""
        messages = [
            {"role": "system", "content": "You are Friday, a helpful AI assistant. and give answer in maximum 5 lines only."},
            {"role": "user", "content": message}
        ]
        
        json_data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        with httpx.Client() as client:
            response = client.post(self.api_url, headers=headers, json=json_data)
            response.raise_for_status()
            return response.json()