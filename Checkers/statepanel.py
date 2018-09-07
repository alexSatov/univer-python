from logic import BoardCell
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QFont, QPen, QBrush
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout


class StatePanel(QWidget):
    def __init__(self, main_window, game, width):
        super().__init__(main_window)
        self.width = width
        self.move(0, width)
        self.painter = QPainter()
        self.fp_label = PlayerLabel(self, game, game.first_player, self.width)
        self.sp_label = PlayerLabel(self, game, game.second_player, self.width)
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.fp_label)
        self.hbox.addWidget(self.sp_label)
        self.setLayout(self.hbox)

    def paintEvent(self, paint_event):
        self.painter.begin(self)
        self.painter.setBrush(QBrush(Qt.SolidPattern))
        self.painter.drawRect(0, 0, self.width, 60)
        self.painter.end()
        self.fp_label.update()
        self.sp_label.update()


class PlayerLabel(QLabel):
    def __init__(self, panel, game, player, width):
        super().__init__(panel)
        self.game = game
        self.player = player
        self.name = 'Player1' if player.checkers_type is BoardCell.fp_checker \
            else 'Player2'
        self.painter = QPainter()
        self.setFixedSize(width / 2 - 10, 60)

    def paintEvent(self, paint_event):
        self.painter.begin(self)
        color = self.color_selection()
        self.painter.setPen(QPen(color))
        self.painter.setFont(QFont('Bold', 14))
        self.painter.drawText(self.rect(), Qt.AlignHCenter, self.name)
        self.painter.end()

    def color_selection(self):
        if self.player.should_make_move:
            if self.player.must_cut():
                    return Qt.red
            else:
                return Qt.green
        else:
            return Qt.white
