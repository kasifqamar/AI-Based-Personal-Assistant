from PyQt5.QtCore import QObject, pyqtSignal
from pathlib import Path
from config import PathConfig

class AnimationHandler(QObject):
    state_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.animations = {
            'idle': str(PathConfig.ANIMATIONS_DIR / 'idle.json'),
            'listening': str(PathConfig.ANIMATIONS_DIR / 'listening.json'),
            'processing': str(PathConfig.ANIMATIONS_DIR / 'processing.json'),
            'error': str(PathConfig.ANIMATIONS_DIR / 'error.json'),
            'speaking': str(PathConfig.ANIMATIONS_DIR / 'speaking.json')
        }
        self.current_state = 'idle'
    def set_state(self, state: str):
        if state in self.animations:
            self.current_state = state
            self.state_changed.emit(state)
    def get_animation_file(self, state: str):
        return self.animations.get(state, self.animations['idle'])
