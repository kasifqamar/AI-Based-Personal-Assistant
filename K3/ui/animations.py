from PyQt5.QtCore import QObject, QPropertyAnimation, QEasingCurve, pyqtProperty, QPoint
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget

class FadeAnimation(QObject):
    def __init__(self, widget, duration=300):
        super().__init__()
        self._opacity = 1.0
        self.widget = widget
        self.animation = QPropertyAnimation(self, b'opacity')
        self.animation.setDuration(duration)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
    @pyqtProperty(float)
    def opacity(self):
        return self._opacity
    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.widget.setWindowOpacity(value)
    def fade_in(self):
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()
    def fade_out(self):
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.start()

class ColorAnimation(QObject):
    def __init__(self, widget, property_name, duration=300):
        super().__init__()
        self.widget = widget
        self.property_name = property_name
        self.animation = QPropertyAnimation(self.widget, self.property_name)
        self.animation.setDuration(duration)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
    def animate(self, start_color, end_color):
        self.animation.setStartValue(start_color)
        self.animation.setEndValue(end_color)
        self.animation.start()

class SlideAnimation(QObject):
    def __init__(self, widget, direction, duration=300):
        super().__init__()
        from PyQt5.QtCore import QPoint
        self.widget = widget
        self.direction = direction.lower()
        self.animation = QPropertyAnimation(self.widget, b'pos')
        self.animation.setDuration(duration)
        self.animation.setEasingCurve(QEasingCurve.OutBack)
    def slide_in(self):
        from PyQt5.QtCore import QPoint
        parent = self.widget.parent()
        end_pos = self.widget.pos()
        if self.direction == 'left':
            start_pos = end_pos - QPoint(self.widget.width(), 0)
        elif self.direction == 'right':
            start_pos = end_pos + QPoint(self.widget.width(), 0)
        elif self.direction == 'top':
            start_pos = end_pos - QPoint(0, self.widget.height())
        else:
            start_pos = end_pos + QPoint(0, self.widget.height())
        self.widget.move(start_pos)
        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(end_pos)
        self.animation.start()
    def slide_out(self):
        from PyQt5.QtCore import QPoint
        start_pos = self.widget.pos()
        if self.direction == 'left':
            end_pos = start_pos - QPoint(self.widget.width(), 0)
        elif self.direction == 'right':
            end_pos = start_pos + QPoint(self.widget.width(), 0)
        elif self.direction == 'top':
            end_pos = start_pos - QPoint(0, self.widget.height())
        else:
            end_pos = start_pos + QPoint(0, self.widget.height())
        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(end_pos)
        self.animation.start()
