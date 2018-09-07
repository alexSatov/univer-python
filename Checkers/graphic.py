from statepanel import StatePanel
from logic import Game, Checker, Player,  BoardCell

from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import QTimer, QRect, QSize, Qt
from PyQt5.QtGui import QPixmap, QPainter, QIcon, QPen


class GameWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.game = Game()
        self.painter = QPainter()
        self.move_timer = QTimer()
        self.item_size = QSize(50, 50)
        self.width = self.game.board_size * 50
        self.height = self.width + 60
        self.state_panel = StatePanel(self, self.game, self.width)
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(self.width, self.height)
        self.setWindowTitle('Checkers')
        self.setWindowIcon(QIcon('Pictures\\logo.png'))

        self.move_timer.timeout.connect(self.bot_move)
        self.move_timer.start(500)

        self.show()

    def paintEvent(self, paint_event):
        self.painter.begin(self)
        self.painter.setPen(QPen(Qt.red, 3))
        self.paint_board()
        self.painter.end()
        self.state_panel.update()

    def paint_board(self):
        self.paint_cells()
        self.paint_checkers()

    def paint_cells(self):
        black_cell = QPixmap('Pictures\\blackCell.png')
        white_cell = QPixmap('Pictures\\whiteCell.png')
        for y in range(self.game.board_size):
            for x in range(self.game.board_size):
                rect = QRect(x * 50, y * 50, 50, 50)
                if (x + y) % 2 == 0:
                    self.painter.drawPixmap(rect, white_cell)
                else:
                    self.painter.drawPixmap(rect, black_cell)

    def paint_checkers(self):
        black_checker = QPixmap('Pictures\\blackChecker.png')
        white_checker = QPixmap('Pictures\\whiteChecker.png')
        blink = QPixmap('Pictures\\blink.png')
        queen = QPixmap('Pictures\\queen.png')
        board = self.game.board
        for y in range(self.game.board_size):
            for x in range(self.game.board_size):
                rect = QRect(x * 50, y * 50, 50, 50)
                if board[y][x] == BoardCell.checker_move:
                    self.painter.drawRect(rect)
                if isinstance(board[y][x], Checker):
                    if board[y][x].type is BoardCell.fp_checker:
                        self.painter.drawPixmap(rect, white_checker)
                    if board[y][x].type is BoardCell.sp_checker:
                        self.painter.drawPixmap(rect, black_checker)
                    if board[y][x].is_active:
                        self.painter.drawPixmap(rect, blink)
                    if board[y][x].is_queen:
                        self.painter.drawPixmap(rect, queen)

    def mousePressEvent(self, mouse_event):
        if isinstance(self.game.active_player, Player):
            x, y = mouse_event.x() // 50, mouse_event.y() // 50
            if self.game.cell_on_board(y, x):
                cell_obj = self.game.board[y][x]
                if type(cell_obj) is Checker:
                    self.game.try_activate(cell_obj)
                if cell_obj is BoardCell.checker_move:
                    self.game.active_player.make_move(y, x)
                    self.check_game_over()
                self.update()

    def keyPressEvent(self, key_event):
        if key_event.key() == 66:  # B
            self.game.move_back()
            self.update()

    def bot_move(self):
        if not self.game.is_over:
            self.game.active_player.choose_move()
            self.update()
            self.check_game_over()

    def check_game_over(self):
        if self.game.is_over:
            self.show_game_over_dialog()

    def show_game_over_dialog(self):
        message = 'Player{} WINS !!!\nAre you want to play again?'.format(
            2 if self.game.is_first_player_move else 1)

        reply = QMessageBox.question(self, 'Game Over', message,
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.Yes)

        if reply == QMessageBox.Yes:
            self.game.start_new_game()
            self.update()
        else:
            exit()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Exit', "Are you sure to exit?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        event.accept() if reply == QMessageBox.Yes else event.ignore()
