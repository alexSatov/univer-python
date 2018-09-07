import sys
from graphic import GameWindow
from PyQt5.QtWidgets import QApplication


if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = GameWindow()
    sys.exit(app.exec())
