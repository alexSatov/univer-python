import os
import sys
import logging
import datetime
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QMainWindow, QApplication,
                             QWidget, QGraphicsScene,
                             QVBoxLayout)

from gameGraphics.gameVisualizer import GameVisualizer, Balls
from gameGraphics.infoPanel import InfoPanel
from gameLogic.game import Game
from gameLogic.gameField import GameField

IMG_PATHS = {Balls.red_ball: "redBall.png", Balls.blue_ball: "blueBall.png",
             Balls.gold_ball: "goldBall.png", Balls.green_ball: "greenBall.png", Balls.pink_ball: "pinkBall.png",
             Balls.purple_ball: "purpleBall.png", Balls.turquoise_ball: "turquoiseBall.png", 0: "tile.png"}

IMG_FOLDER_PATH = os.path.join(os.path.curdir, "Images")


class MainWindow(QMainWindow):
    def __init__(self, sceen_size):
        super().__init__()
        self.mainWidget = QWidget()
        self.pixmaps = self.load_pixmaps()
        game_field = GameField(9, 9)
        self.game = Game(game_field)
        self.game_visualizer = GameVisualizer(self, QGraphicsScene(), sceen_size)
        self.tools_panel = InfoPanel(self)
        self.game_visualizer.scene.selectionChanged.connect(self.tools_panel.update)
        self.vertical_layout = QVBoxLayout()

        self.set_default_state()
        self.show()

    def set_default_state(self):
        self.setFixedSize(620, 680)
        self.setWindowTitle("Lines")
        self.vertical_layout.addWidget(self.tools_panel)
        self.vertical_layout.addWidget(self.game_visualizer)
        self.mainWidget.setLayout(self.vertical_layout)
        self.setCentralWidget(self.mainWidget)

    def load_pixmaps(self):
        pixmaps = {}
        for code, path in IMG_PATHS.items():
            img_path = os.path.join(IMG_FOLDER_PATH, path)
            if os.path.exists(img_path):
                pixmaps[code] = QPixmap(img_path)
        return pixmaps


def print_help():
    with open('help.txt', encoding="utf-8") as help_file:
        logging.debug("Successfully opened help file: ")
        for text_line in help_file:
            print(text_line)


def is_help_command():
    return len(sys.argv) > 1 and sys.argv[1] in {'/?', '--help', "-h"}


if __name__ == '__main__':
    if is_help_command():
        print_help()
    else:
        app = QApplication(sys.argv)
        screen = app.primaryScreen()
        ex = MainWindow(screen.size())
        sys.exit(app.exec_())
