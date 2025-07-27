import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from config import UIConfig

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(UIConfig.WINDOW_TITLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()