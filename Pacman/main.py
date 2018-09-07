import sys
import filechecker
from logic import Game
from graphic import GameField
from statistics import StatisticsPanel
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtWidgets import QWidget, QApplication


class GameWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.game = Game()
        arg_parsing(self.game)
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


def arg_parsing(game):
    if len(sys.argv) == 2:
        command = sys.argv[1]
        check_command(game, command)
    elif len(sys.argv) > 2:
        print('Too many arguments')
        sys.exit()


def check_command(game, command):
    if command in {'/?', '--help', '-h'}:
        print_help()
    elif command in {'rec', '-r'}:
        print_records()
    elif command in {'god', 'level2', 'level3'}:
        game.cheat(command)
    else:
        print('Incorrect command')
        sys.exit()


def print_help():
    with open('help.txt') as help_file:
        for text_line in help_file:
            print(text_line)
    sys.exit()


def print_records():
    with open('records.txt') as records_file:
        for text_line in records_file:
            print(text_line)
    sys.exit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GameWindow()
    sys.exit(app.exec())
