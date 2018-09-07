from PyQt5.QtWidgets import QWidget, QInputDialog


class GameOverDialog(QInputDialog):
    def __init__(self, game, title, parent=None):
        super().__init__(parent)
        self.widget = QWidget()
        self.setWindowTitle(title)
        self.setLabelText("Your result: {0}. ".format(game.user_scores))
        self.game = game
        self.setOkButtonText("Exit")
        self.setCancelButtonText("Try again")
        self.setWindowModality(0)
        self.setModal(False)
        self.show()