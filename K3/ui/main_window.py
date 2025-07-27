import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QSplitter, QStatusBar, QScrollArea, QFrame, QGroupBox, 
                            QLabel, QLineEdit)
from PyQt5.QtCore import Qt, QSize, QTimer, QTime
from PyQt5.QtGui import QFont, QPixmap
from qt_material import apply_stylesheet
from config import UIConfig, PathConfig
from modules.assistant_core import FridayAssistant
from ui.widgets import (ChatBubble, AnimatedButton, CommandInput,
                       WeatherWidget, NewsWidget)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.assistant = FridayAssistant()
        self.setup_ui()
        self.setup_connections()
        self.apply_styles()
        self.update_weather()
        self.update_news()
        # Connect reminder signal
        self.assistant.reminder.reminder_triggered.connect(self.show_reminder_notification)
        
        # Setup clock timer
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)  # Update every second
        self.update_clock()

    def setup_ui(self):
        self.setWindowTitle(UIConfig.WINDOW_TITLE)
        self.setMinimumSize(1000, 700)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(2)

        # Left panel (chat)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setStyleSheet("background-color: #2a2a2a;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 10, 15, 10)
        title = QLabel("Friday AI Assistant")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        left_layout.addWidget(header, 0)

        # Chat area
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(10)
        self.chat_layout.setContentsMargins(15, 15, 15, 15)
        self.chat_scroll.setWidget(self.chat_container)

        # Welcome message
        welcome_msg = QLabel("You want to know the current information!")
        welcome_msg.setStyleSheet("font-size: 14px; color: #aaaaaa;")
        self.chat_layout.addWidget(welcome_msg)

        # Input area
        input_widget = QWidget()
        input_widget.setStyleSheet("background-color: #2a2a2a;")
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(15, 15, 15, 15)
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Type your command here...")
        self.command_input.setMaximumHeight(60)
        self.command_input.setStyleSheet("""
            QLineEdit {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #4a4a4a;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
        """)
        self.mic_button = AnimatedButton(str(PathConfig.ICONS_DIR / "mic.png"))
        self.mic_button.setFixedSize(40, 40)
        input_layout.addWidget(self.command_input, 1)
        input_layout.addWidget(self.mic_button, 0, Qt.AlignRight)

        left_layout.addWidget(self.chat_scroll, 1)
        left_layout.addWidget(input_widget, 0)

        # Right panel
        right_panel = QWidget()
        right_panel.setStyleSheet("background-color: #252525;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(15)

        # Current group box
        current_group = QGroupBox("Current")
        current_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: white;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        current_layout = QVBoxLayout(current_group)

        # Clock widget
        clock_widget = QWidget()
        clock_layout = QVBoxLayout(clock_widget)
        clock_title = QLabel("CLOCK")
        clock_title.setStyleSheet("font-size: 12px; color: #aaaaaa;")
        clock_layout.addWidget(clock_title)
        self.clock_label = QLabel()
        self.clock_label.setAlignment(Qt.AlignCenter)
        self.clock_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        clock_layout.addWidget(self.clock_label)
        current_layout.addWidget(clock_widget)

        # Weather widget
        weather_widget = QWidget()
        weather_layout = QVBoxLayout(weather_widget)
        weather_title = QLabel("WEATHER")
        weather_title.setStyleSheet("font-size: 12px; color: #aaaaaa;")
        weather_layout.addWidget(weather_title)
        self.weather_widget = WeatherWidget()
        weather_layout.addWidget(self.weather_widget)
        current_layout.addWidget(weather_widget)

        # News widget
        news_widget = QWidget()
        news_layout = QVBoxLayout(news_widget)
        news_title = QLabel("NEWS")
        news_title.setStyleSheet("font-size: 12px; color: #aaaaaa;")
        news_layout.addWidget(news_title)
        self.news_widget = NewsWidget()
        news_layout.addWidget(self.news_widget)
        current_layout.addWidget(news_widget)

        right_layout.addWidget(current_group)
        right_layout.addStretch(1)

        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([700, 300])
        main_layout.addWidget(splitter)

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("background-color: #2a2a2a; color: white;")
        self.setStatusBar(self.status_bar)

    def show_reminder_notification(self, name: str, message: str):
        """Show a reminder notification in the chat"""
        notification = f"⏰ REMINDER: {name}\n{message}"
        self.add_chat_message(notification, is_user=False)
        self.assistant.speak(f"Reminder: {message}")

    def update_clock(self):
        """Update the clock display with current time"""
        current_time = QTime.currentTime()
        time_text = current_time.toString("hh:mm:ss AP")
        self.clock_label.setText(time_text)

    def setup_connections(self):
        self.command_input.returnPressed.connect(self.process_command)
        self.mic_button.clicked.connect(self.handle_voice_input)

    def handle_voice_input(self):
        """Handle voice input with proper feedback"""
        self.status_bar.showMessage("Listening...", 2000)
        text = self.assistant.listen_to_voice()
        if text and not any(err in text.lower() for err in ["error", "sorry", "hear"]):
            self.command_input.setText(text)
            self.process_command()
        elif text:
            self.add_chat_message(text, is_user=False)
            self.status_bar.showMessage("Voice command processed", 2000)

    def process_command(self):
        """Process and display commands"""
        command = self.command_input.text().strip()
        if not command:
            return
        self.add_chat_message(command, is_user=True)
        self.command_input.clear()

        # Handle time queries separately
        if any(word in command.lower() for word in ["time", "current time", "what time is it", "tell me the time"]):
            self.speak_time_only()
            return

        response = self.assistant.process_command(command)
        self.add_chat_message(response, is_user=False)

        if "weather" in command.lower():
            self.update_weather()
        elif "news" in command.lower():
            self.update_news()

    def speak_time_only(self):
        """Speak the current time without showing in chat"""
        current_time = QTime.currentTime()
        time_text = current_time.toString("h:mm AP")
        # Speak the time
        self.assistant.speak(f"The current time is {time_text}")
        # Brief feedback
        self.status_bar.showMessage(f"Time spoken: {time_text}", 3000)

    def add_chat_message(self, text: str, is_user: bool):
        """Add message bubble to chat area"""
        bubble = ChatBubble(text, is_user)
        self.chat_layout.addWidget(bubble)
        # Scroll to bottom
        self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()
        )
        bubble.show()

    def update_weather(self):
        data = self.assistant.weather.get_current_weather()
        self.weather_widget.update_weather(data)

    def update_news(self):
        news = self.assistant.news.get_news()
        self.news_widget.update_news(news)

    def apply_styles(self):
        """Apply modern UI styling"""
        theme = "dark_teal.xml" if UIConfig.THEME == "dark" else "light_teal.xml"
        apply_stylesheet(self, theme=theme)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #2a2a2a;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #4a4a4a;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

# Don't forget to import your reminder signal connection somewhere in your setup
# e.g., if your ReminderModule has a signal called 'reminder_triggered':
# self.assistant.reminder.reminder_triggered.connect(self.show_reminder_notification)

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())