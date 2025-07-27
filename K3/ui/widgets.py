from PyQt5.QtWidgets import QWidget, QLabel, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame, QSizePolicy
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont
from config import UIConfig
from PyQt5.QtGui import QIcon

class ChatBubble(QLabel):
    def __init__(self, text, is_user, parent=None):
        super().__init__(parent)
        self.setWordWrap(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMargin(10)
        if is_user:
            self.setStyleSheet('background-color:#0078d4; color:white; border-radius:10px; padding:8px;')
            self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        else:
            self.setStyleSheet('background-color:#f3f3f3; color:black; border-radius:10px; padding:8px;')
            self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setText(text)

class AnimatedButton(QPushButton):
    def __init__(self, icon_path, text='', parent=None):
        super().__init__(text, parent)
        self.setIconSize(QSize(32,32))
        self.setFixedSize(50,50)
        self.setStyleSheet('''
            QPushButton {
                border-radius:25px; background-color:#0078d4; border:none;
            }
            QPushButton:hover {
                background-color:#005a9e;
            }
            QPushButton:pressed {
                background-color:#004578;
            }
        ''')
        self.setIcon(QIcon(icon_path))
        
class CommandInput(QTextEdit):
    returnPressed = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Type your command here...")
        self.setFixedHeight(60)
        self.setStyleSheet('''
            QTextEdit {
                border:1px solid #ccc; border-radius:5px; padding:5px; font-size:14px;
            }
        ''')
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and not event.modifiers():
            self.returnPressed.emit()
        else:
            super().keyPressEvent(event)
class WeatherWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 10px;
            }
            QLabel {
                color: #ffffff;
            }
        """)
        layout = QVBoxLayout()
        self.title = QLabel('Weather')
        self.title.setFont(QFont(UIConfig.FONT_FAMILY, 12, QFont.Bold))
        self.weather_icon = QLabel()
        self.weather_icon.setFixedSize(64,64)
        self.temperature = QLabel()
        self.temperature.setFont(QFont(UIConfig.FONT_FAMILY, 24))
        self.description = QLabel()
        self.description.setFont(QFont(UIConfig.FONT_FAMILY, 10))
        self.details = QLabel()
        self.details.setFont(QFont(UIConfig.FONT_FAMILY, 9))
        layout.addWidget(self.title)
        layout.addWidget(self.weather_icon)
        layout.addWidget(self.temperature)
        layout.addWidget(self.description)
        layout.addWidget(self.details)
        self.setLayout(layout)
    def update_weather(self, weather_data):
        if not weather_data:
            return
        self.temperature.setText(f"{weather_data['main']['temp']}C")
        self.description.setText(weather_data['weather'][0]['description'].capitalize())
        self.details.setText(f"Humidity: {weather_data['main']['humidity']}%\nWind: {weather_data['wind']['speed']} m/s")
        
class NewsWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 10px;
            }
            QLabel {
                color: #ffffff;
            }
        """)
        layout = QVBoxLayout()
        self.title = QLabel('Latest News')
        self.title.setFont(QFont(UIConfig.FONT_FAMILY, 12, QFont.Bold))
        self.news_list = QVBoxLayout()
        self.news_list.setSpacing(5)
        layout.addWidget(self.title)
        layout.addLayout(self.news_list)
        self.setLayout(layout)
    def update_news(self, news_items):
        while self.news_list.count():
            item = self.news_list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for item in news_items[:3]:
            lbl = QLabel(item['title'])
            lbl.setWordWrap(True)
            lbl.setStyleSheet('''
                QLabel { padding:5px; border-bottom:1px solid #eee; }
                QLabel:hover { background-color:#f0f0f0; }
            ''')
            self.news_list.addWidget(lbl)
