from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtWidgets import QLabel


class NextBallsLabel(QLabel):
    def __init__(self, parent, game):
        super().__init__(parent)
        self.game = game
        self.pixmaps = parent.pixmaps
        self.painter = QPainter()
        self.setFixedSize(200, parent.height())

    def init_start_state(self):
        self.painter.setPen(QColor(255, 255, 255))
        self.painter.setFont(QFont('Cursive', 12))

    def paintEvent(self, paint_event):
        self.painter.begin(self)
        self.painter.drawText(self.rect(), Qt.AlignLeft, "Next balls:")

        x_pos = 70
        for ball_id in self.game.next_balls_color:
            pixmap = self.pixmaps[ball_id]
            self.painter.drawPixmap(x_pos, 0, 24, 24, pixmap)
            x_pos += 25
        self.painter.end()
