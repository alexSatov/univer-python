from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt


class StatisticsPanel(QWidget):
    def __init__(self, parent, game):
        super().__init__(parent)
        self.move(0, 608)

        self.scores = Scores(self, game)
        self.lives = Lives(self, game)

        self.horizontal_layout = QHBoxLayout()
        self.horizontal_layout.addWidget(self.scores)
        self.horizontal_layout.addWidget(self.lives)
        self.setLayout(self.horizontal_layout)

    def paintEvent(self, paint_event):
        self.scores.update()


class Scores(QLabel):
    def __init__(self, parent, game):
        super().__init__(parent)
        self.game = game
        self.painter = QPainter()
        self.setFixedSize(152, 52)

    def paintEvent(self, QPaintEvent):
        self.painter.begin(self)
        self.painter.setPen(QColor(255, 255, 255))
        self.painter.setFont(QFont('Cursive', 15))
        self.painter.drawText(self.rect(), Qt.AlignLeft, "Scores: {0}".format(self.game.pacman.scores))
        self.painter.end()


class Lives(QLabel):
    def __init__(self, parent, game):
        super().__init__(parent)
        self.game = game
        self.painter = QPainter()
        self.setFixedSize(152, 52)
        self.pacman_image = QPixmap("logo.png")
        self.x_pos = 70

    def paintEvent(self, paint_event):
        self.painter.begin(self)
        self.painter.setPen(QColor(255, 255, 255))
        self.painter.setFont(QFont('Cursive', 15))
        self.painter.drawText(self.rect(), Qt.AlignLeft, "Lives:")

        for i in range(self.game.pacman.lifes):
            self.painter.drawPixmap(self.x_pos, 0, 32, 32, self.pacman_image)
            self.x_pos += 40

        self.x_pos = 70
        self.painter.end()
