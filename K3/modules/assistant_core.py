import re
import threading
import platform
import subprocess
import os
from typing import Optional, Dict, Any
from datetime import datetime
from config import AssistantConfig
from modules.json_db import db
from modules.system_control import SystemControl
from modules.weather import WeatherModule
from modules.news import NewsModule
from modules.chat import ChatModule
from modules.animation_handler import AnimationHandler
import speech_recognition as sr
import pyttsx3
from gtts import gTTS
import tempfile
import time
from modules.reminder import ReminderModule

class FridayAssistant:
    def __init__(self):
        self.system = SystemControl()
        self.weather = WeatherModule()
        self.news = NewsModule()
        self.chat = ChatModule()
        self.animation = AnimationHandler()
        self.reminder = ReminderModule()
        
        # Application mapping for different operating systems
        self.app_mapping = {
            'chrome': {
                'windows': 'start chrome',
                'linux': 'google-chrome',
                'darwin': 'open -a "Google Chrome"'
            },
            'youtube': {
                'windows': 'start https://youtube.com',
                'linux': 'xdg-open https://youtube.com',
                'darwin': 'open https://youtube.com'
            },
            'notepad': {
                'windows': 'notepad',
                'linux': 'gedit',
                'darwin': 'open -a TextEdit'
            }
        }
        
        self.current_state = "idle"
        self.command_handlers = {
            "system": self._handle_system_command,
            "weather": self._handle_weather_command,
            "news": self._handle_news_command,
            "chat": self._handle_chat_command,
            "reminder": self._handle_reminder_command
        }

        self.command_patterns = {
            "system": r"(open|launch|start|close|quit|exit|shutdown|restart|sleep|volume|mute|unmute|play|pause|stop)",
            "weather": r"(weather|temperature|forecast|humidity|wind|rain|snow)",
            "news": r"(news|headlines|articles|read|latest|update)",
            "reminder": r"(reminder|remind me|alarm|timer)"
        }

        # Enhanced voice setup
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self._setup_voice_engine()

    def _setup_voice_engine(self):
        """Initialize voice recognition and TTS with proper error handling"""
        try:
            # Calibrate microphone
            with self.microphone as source:
                print("Calibrating microphone...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            # Initialize TTS
            if AssistantConfig.VOICE_ENGINE == "pyttsx3":
                self.tts_engine = pyttsx3.init()
                voices = self.tts_engine.getProperty('voices')
                self.tts_engine.setProperty('voice', voices[0].id)
                self.tts_engine.setProperty('rate', 150)
            else:
                self.tts_engine = None
        except Exception as e:
            print(f"Voice setup error: {e}")
            AssistantConfig.VOICE_ENABLED = False

    def speak(self, text: str):
        """Speak text with proper error handling"""
        if not AssistantConfig.VOICE_ENABLED:
            return
            
        self._set_state("speaking")
        try:
            if AssistantConfig.VOICE_ENGINE == "pyttsx3" and self.tts_engine:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            else:  # Fallback to gTTS
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    tts = gTTS(text=text, lang='en')
                    tts.save(f.name)
                    if os.name == 'nt':  # Windows
                        os.system(f"start {f.name}")
                    else:  # Linux/Mac
                        os.system(f"mpg123 {f.name}")
                    time.sleep(1)  # Wait for playback
        except Exception as e:
            print(f"Speech error: {e}")
        finally:
            self._set_state("idle")

    def listen_to_voice(self) -> Optional[str]:
        """Listen to voice input with robust error handling"""
        if not AssistantConfig.VOICE_ENABLED:
            return "Voice input is disabled"
            
        self._set_state("listening")
        try:
            with self.microphone as source:
                print("Listening... (speak now)")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
            text = self.recognizer.recognize_google(audio)
            print(f"Recognized: {text}")
            return text
        except sr.WaitTimeoutError:
            return "I didn't hear anything. Please try again."
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand that."
        except sr.RequestError as e:
            return f"Speech service error: {str(e)}"
        except Exception as e:
            return f"Voice recognition error: {str(e)}"
        finally:
            self._set_state("idle")

    def process_command(self, command: str) -> str:
        """Process user command and return response"""
        self._set_state("processing")
        command_lower = command.lower()
        command_type = self._identify_command_type(command_lower)
        
        # Handle the command
        if command_type in self.command_handlers:
            response = self.command_handlers[command_type](command)
        else:
            response = self._handle_chat_command(command)
        
        # Add to chat history
        db.add_chat_message("user", command)
        db.add_chat_message("assistant", response)
        
        # Speak the response
        if AssistantConfig.VOICE_ENABLED:
            self.speak(response)
        
        self._set_state("idle")
        return response

    def _identify_command_type(self, command: str) -> str:
        """Detect command type based on regex patterns"""
        for cmd_type, pattern in self.command_patterns.items():
            if re.search(pattern, command):
                return cmd_type
        return "chat"

    def _handle_system_command(self, command: str) -> str:
        """Handle system-related commands with improved app opening"""
        command_lower = command.lower()
        
        # Open applications
        if any(word in command_lower for word in ["open", "launch", "start"]):
            app = self._extract_app_name(command_lower)
            if app:
                try:
                    system_name = platform.system().lower()
                    if system_name not in ['windows', 'linux', 'darwin']:
                        system_name = 'windows'  # default fallback
                    
                    app_cmd = self.app_mapping.get(app, {}).get(system_name)
                    
                    if app_cmd:
                        if system_name == 'windows' and app_cmd.startswith('start '):
                            os.system(app_cmd)
                        else:
                            subprocess.Popen(app_cmd, shell=True)
                        return f"Opening {app} for you."
                    else:
                        return f"No command found to open {app} on {system_name}"
                except Exception as e:
                    return f"Failed to open {app}: {str(e)}"
            return "I couldn't determine which application to open."

        elif "volume" in command_lower:
            if "up" in command_lower or "increase" in command_lower:
                self.system.increase_volume()
                return "Increasing volume."
            elif "down" in command_lower or "decrease" in command_lower:
                self.system.decrease_volume()
                return "Decreasing volume."
            elif "mute" in command_lower:
                self.system.mute_volume()
                return "Volume muted."
            elif "unmute" in command_lower:
                self.system.unmute_volume()
                return "Volume unmuted."
            else:
                return "Please specify volume action (up/down/mute/unmute)."

        elif any(word in command_lower for word in ["play", "pause", "stop"]):
            if "play" in command_lower:
                self.system.play_media()
                return "Playing media."
            elif "pause" in command_lower:
                self.system.pause_media()
                return "Media paused."
            else:
                self.system.stop_media()
                return "Media stopped."

        elif any(word in command_lower for word in ["shutdown", "restart", "sleep"]):
            if "shutdown" in command_lower:
                self.system.shutdown()
                return "Shutting down system."
            elif "restart" in command_lower:
                self.system.restart()
                return "Restarting system."
            else:
                self.system.sleep()
                return "Putting system to sleep."

        return "I didn't understand that system command."

    def _extract_app_name(self, command: str) -> Optional[str]:
        """Extract application name from command using app mapping"""
        for app_name in self.app_mapping.keys():
            if app_name in command:
                return app_name
        return None

    def _handle_weather_command(self, command: str) -> str:
        """Handle weather-related requests"""
        location = None
        if "in" in command:
            parts = command.split("in")
            if len(parts) > 1:
                location = parts[-1].strip()

        if "forecast" in command.lower():
            forecast = self.weather.get_weather_forecast(location)
            return self._format_forecast_response(forecast)
        else:
            weather = self.weather.get_current_weather(location)
            return self._format_weather_response(weather)

    def _format_weather_response(self, weather_data: Dict[str, Any]) -> str:
        """Present current weather data"""
        if not weather_data:
            return "Sorry, I couldn't fetch the weather data."
        city = weather_data.get("name", "Unknown location")
        temp = weather_data.get("main", {}).get("temp", "unknown")
        desc = weather_data.get("weather", [{}])[0].get("description", "")
        humidity = weather_data.get("main", {}).get("humidity", "")
        wind = weather_data.get("wind", {}).get("speed", "")
        return (f"The weather in {city} is currently {desc}. "
                f"Temperature is {temp}°C, humidity is {humidity}%, "
                f"and wind speed is {wind} m/s.")

    def _format_forecast_response(self, forecast_data: Dict[str, Any]) -> str:
        """Present weather forecast data"""
        if not forecast_data or not forecast_data.get("list"):
            return "Sorry, I couldn't fetch the forecast data."
        city = forecast_data.get("city", {}).get("name", "Unknown location")
        forecasts = forecast_data["list"][:4]  # Next intervals
        response = f"Weather forecast for {city}:\n"
        for forecast in forecasts:
            time_str = datetime.fromtimestamp(forecast["dt"]).strftime("%H:%M")
            temp = forecast["main"]["temp"]
            desc = forecast["weather"][0]["description"]
            response += f"{time_str}: {desc}, {temp}°C\n"
        return response

    def _handle_news_command(self, command: str) -> str:
        """Fetch news based on category or recency"""
        category = None
        for cat in ["technology", "science", "business", "sports", "entertainment"]:
            if cat in command.lower():
                category = cat
                break

        count = 3  # default
        if "latest" in command.lower() or "recent" in command.lower():
            count = 1

        news_items = self.news.get_news(category=category, count=count)
        return self._format_news_response(news_items)

    def _format_news_response(self, news_items: list) -> str:
        """Format news headlines"""
        if not news_items:
            return "Sorry, I couldn't fetch any news at the moment."
        response = "Here are the latest news headlines:\n"
        for i, item in enumerate(news_items[:3], 1):
            response += f"{i}. {item.get('title', 'No title')}\n"
        return response

    def _handle_chat_command(self, command: str) -> str:
        """Handle general chat responses"""
        try:
            return self.chat.get_response(command)
        except Exception as e:
            return f"Error processing chat: {str(e)}"

    def _set_state(self, state: str):
        """Update assistant state and trigger animations"""
        self.current_state = state
        self.animation.set_state(state)

    def _handle_reminder_command(self, command: str) -> str:
        """Enhanced reminder command handler"""
        command_lower = command.lower()

        # List reminders
        if any(word in command_lower for word in ["list reminders", "show reminders", "what are my reminders"]):
            reminders = self.reminder.get_reminders()
            if not reminders:
                return "You have no upcoming reminders."
            response = "⏰ Your upcoming reminders:\n"
            for i, rem in enumerate(reminders, 1):
                time_str = datetime.fromisoformat(rem['trigger_time']).strftime("%I:%M %p on %b %d")
                response += f"{i}. {rem['name']} - {time_str}\n   {rem['message']}\n"
            return response

        # Cancel reminder
        if any(word in command_lower for word in ["cancel", "delete", "remove"]):
            name = None
            # Try to extract the reminder name
            for phrase in ["reminder called", "reminder named", "reminder"]:
                if phrase in command_lower:
                    parts = command_lower.split(phrase)
                    if len(parts) > 1:
                        name = parts[1].strip()
                        break
            if not name:
                # Try to get name after cancel/delete/remove
                for word in ["cancel", "delete", "remove"]:
                    if word in command_lower:
                        parts = command_lower.split(word)
                        if len(parts) > 1:
                            name = parts[1].strip()
                            break
            if name:
                if self.reminder.remove_reminder(name):
                    return f"✅ Reminder '{name}' has been canceled."
                return f"❌ No reminder found with name '{name}'."
            return "Please specify which reminder to cancel (e.g., 'cancel reminder call mom')."

        # Create new reminder
        name, message, time_str = self.reminder.extract_reminder_info(command)
        if not all([name, message, time_str]):
            return ("Please specify a reminder with format:\n"
                    "'Remind me to [task] at [time]'\n"
                    "Examples:\n"
                    "- Remind me to call mom at 3pm\n"
                    "- Set reminder for meeting in 30 minutes\n"
                    "- Team standup at 9:30 AM tomorrow")
        
        trigger_time = self.reminder.parse_reminder_time(time_str)
        if not trigger_time:
            return f"Sorry, I couldn't understand the time '{time_str}'. Try formats like '3pm' or 'in 30 minutes'."
        
        if self.reminder.add_reminder(name, message, trigger_time):
            time_formatted = trigger_time.strftime("%I:%M %p on %b %d")
            return f"✅ Reminder set!\n'{message}' at {time_formatted}"
        return f"A reminder with name '{name}' already exists."
