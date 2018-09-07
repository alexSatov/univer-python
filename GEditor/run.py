import sys
from graphics import MainWindow
from PyQt5.QtWidgets import QApplication


if __name__ == '__main__':
    app = QApplication(sys.argv)
    png_parser_window = MainWindow()
    sys.exit(app.exec())
