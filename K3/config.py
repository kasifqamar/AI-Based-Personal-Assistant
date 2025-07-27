import os
from pathlib import Path

# Base directory for relative paths
BASE_DIR = Path(__file__).parent.resolve()

class APIConfig:
    OPENWEATHER_API_KEY = "5e380a740a7dd2d078ac8801c8d81511"
    GROQ_API_KEY = "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"
    NEWS_API_KEY = "f26a3376aa614254aa547d03e3105a0c"  # replace with your actual NewsAPI key

    OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
    CURRENT_WEATHER_URL = f"{OPENWEATHER_BASE_URL}/weather"
    FORECAST_URL = f"{OPENWEATHER_BASE_URL}/forecast"

    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    NEWS_API_URL = "https://newsapi.org/v2/top-headlines"


class PathConfig:
    ASSETS_DIR = BASE_DIR / "assets"
    ANIMATIONS_DIR = ASSETS_DIR / "animations"
    ICONS_DIR = ASSETS_DIR / "icons"
    STYLES_DIR = ASSETS_DIR / "styles"

    DATABASE_DIR = BASE_DIR / "database"
    USER_DATA_FILE = DATABASE_DIR / "user_data.json"
    DATA_DIR = BASE_DIR / "data"
    DATABASE_DIR = BASE_DIR / "database"
    os.makedirs(DATABASE_DIR, exist_ok=True)


class UIConfig:
    WINDOW_TITLE = "Friday AI Assistant"
    WINDOW_SIZE = (800, 600)
    THEME = "dark"
    FONT_FAMILY = "Arial"
    FONT_SIZE = 12
    ANIMATION_DURATION = 300  # milliseconds


class AssistantConfig:
    DEFAULT_CITY = "New York"
    DEFAULT_COUNTRY = "US"
    DEFAULT_NEWS_CATEGORY = "technology"
    DEFAULT_NEWS_LANGUAGE = "en"
    DEFAULT_NEWS_COUNT = 5

    VOICE_ENABLED = True
    VOICE_ENGINE = "pyttsx3"
    VOICE_TIMEOUT = 5  # seconds to wait for voice input
