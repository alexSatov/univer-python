from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtWidgets import QLabel


class Scores(QLabel):
    def __init__(self, parent, game):
        super().__init__(parent)
        self.game = game
        self.painter = QPainter()
        self.setFixedSize(200, parent.height())
        self.init_start_state()

    def init_start_state(self):
        self.painter.setPen(QColor(255, 255, 255))
        self.painter.setFont(QFont('Cursive', 12))

    def paintEvent(self, QPaintEvent):
        self.painter.begin(self)
        info_str = "Scores: {0}".format(self.game.user_scores)
        self.painter.drawText(self.rect(), Qt.AlignLeft, info_str)
        self.painter.end()