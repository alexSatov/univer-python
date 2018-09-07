import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPalette, QColor, QIcon
from graphic import GameField
from logic import Game
from statistics import StatisticsPanel


class GameWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.game = Game()
        self.game_field = GameField(self, self.game)
        self.statistics_panel = StatisticsPanel(self, self.game)
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(608, 660)
        self.setWindowTitle('Pacman')
        self.setWindowIcon(QIcon("logo.png"))
        self.game_field.setFixedSize(608, 608)
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0))
        self.setPalette(palette)
        self.show()

    def paintEvent(self, QPaintEvent):
        self.statistics_panel.update()


def is_help_command():
    return sys.argv[1] in {'/?', '--help'}


def print_help():
    with open('help.txt') as help_file:
        for text_line in help_file:
            print(text_line)


def is_records_command():
    return sys.argv[1] in {'rec', '-r'}


def print_records():
    with open('records.txt') as records_file:
        for text_line in records_file:
            print(text_line)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if is_help_command():
            print_help()
        if is_records_command():
            print_records()
    else:
        app = QApplication(sys.argv)
        ex = GameWindow()
        sys.exit(app.exec_())
