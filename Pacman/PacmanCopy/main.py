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
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(608, 660)
        self.setWindowTitle('Pacman')
        self.setWindowIcon(QIcon("logo.png"))
        self.game_field = GameField(self, self.game)
        self.game_field.setFixedSize(608, 608)
        self.statistics_panel = StatisticsPanel(self, self.game)

        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0))
        self.setPalette(palette)
        self.show()

    def paintEvent(self, QPaintEvent):
        self.statistics_panel.update()


def is_help_command():
    return len(sys.argv) > 1 and sys.argv[1] in {'/?', '--help'}


def print_help():
    with open('help.txt', encoding="utf-8") as help_file:
        for text_line in help_file:
            print(text_line)

if __name__ == '__main__':
    if is_help_command():
        print_help()
    else:
        app = QApplication(sys.argv)
        try:
            ex = GameWindow()
            print_help()
        except FileNotFoundError as error:
            print("ERROR: file {0} for sprite animation doesn't exist."
                  "Please try to recover this file "
                  "in folder Images".format(error.args[0]))
        sys.exit(app.exec_())
