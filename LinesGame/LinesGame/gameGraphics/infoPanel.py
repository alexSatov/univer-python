from gameGraphics.scoresLabel import Scores
from gameGraphics.nextBallsLabel import NextBallsLabel
from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QPushButton


class InfoPanel(QGroupBox):
    def __init__(self, parent):
        super().__init__(parent.mainWidget)
        layout = QHBoxLayout()
        self.pixmaps = parent.pixmaps
        self.game = parent.game
        self.setLayout(layout)
        self.scores = Scores(self, self.game)
        self.next_balls = NextBallsLabel(self, self.game)
        layout.addWidget(self.scores)
        layout.addWidget(self.next_balls)
        # self.undo_button = QPushButton("undo action", self)
        # self.undo_button.clicked.connect(self.game.undo_action)
        # self.undo_button.clicked.connect(parent.game_visualizer.update)
        # layout.addWidget(self.undo_button)


    def paintEvent(self, paint_event):
        self.scores.update()
        self.next_balls.update()


