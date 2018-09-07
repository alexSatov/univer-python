import sys
from logic import BoardCell
from PyQt5.QtCore import QRect, QSize
from PyQt5.QtGui import QPixmap, QPainter, QIcon
from PyQt5.QtWidgets import QFileDialog, QWidget, QMessageBox, QPushButton, \
    QApplication


class Config(QWidget):
    def __init__(self):
        super().__init__()
        self.board_size = self.get_fixed_size()
        self.board = []
        self.create_board()
        self.checkers_type = None
        self.is_saved = True
        self.painter = QPainter()
        self.item_size = QSize(50, 50)
        self.width = self.board_size * 50
        self.height = self.width + 60
        self.white_checker_button = QPushButton('', self)
        self.black_checker_button = QPushButton('', self)
        self.init_ui()

    @staticmethod
    def get_fixed_size():
        size = int(input('Write board size (3 < n < 101, n - even) '))
        if size % 2 == 0 and 3 < size < 101:
            return size
        print('Incorrect size')
        exit()

    def create_board(self):
        for y in range(self.board_size):
            self.board.append([])
            for x in range(self.board_size):
                self.board[y].append(BoardCell.empty)

    def init_ui(self):
        self.setFixedSize(self.width, self.height)
        self.setWindowTitle('Board Config')
        self.setWindowIcon(QIcon('Pictures/logo.png'))

        black_checker = QIcon('Pictures/blackChecker.png')
        white_checker = QIcon('Pictures/whiteChecker.png')

        self.white_checker_button.setIcon(white_checker)
        self.white_checker_button.move(self.width * 0.5 - 95, self.height - 50)
        self.white_checker_button.clicked.connect(self.set_white_checker)
        self.white_checker_button.setFixedSize(40, 40)

        self.black_checker_button.setIcon(black_checker)
        self.black_checker_button.move(self.width * 0.5 - 45, self.height - 50)
        self.black_checker_button.clicked.connect(self.set_black_checker)
        self.black_checker_button.setFixedSize(40, 40)

        save_button = QPushButton('Save', self)
        save_button.move(self.width * 0.5 + 10, self.height - 45)
        save_button.clicked.connect(self.save_file)
        save_button.setFixedSize(80, 28)

    def set_white_checker(self):
        self.checkers_type = BoardCell.fp_checker
        self.white_checker_button.setDown(False if self.white_checker_button
                                          .isDown() else True)

    def set_black_checker(self):
        self.checkers_type = BoardCell.sp_checker
        self.black_checker_button.setDown(False if self.black_checker_button
                                          .isDown() else True)

    def paintEvent(self, paint_event):
        self.painter.begin(self)
        self.paint_board()
        self.painter.end()

    def paint_board(self):
        self.paint_cells()
        self.paint_checkers()

    def paint_cells(self):
        black_cell = QPixmap('Pictures\\blackCell.png')
        white_cell = QPixmap('Pictures\\whiteCell.png')
        for y in range(self.board_size):
            for x in range(self.board_size):
                rect = QRect(x * 50, y * 50, 50, 50)
                if (x + y) % 2 == 0:
                    self.painter.drawPixmap(rect, white_cell)
                else:
                    self.painter.drawPixmap(rect, black_cell)

    def paint_checkers(self):
        black_checker = QPixmap('Pictures\\blackChecker.png')
        white_checker = QPixmap('Pictures\\whiteChecker.png')
        for y in range(self.board_size):
            for x in range(self.board_size):
                rect = QRect(x * 50, y * 50, 50, 50)
                if self.board[y][x] is BoardCell.fp_checker:
                    self.painter.drawPixmap(rect, white_checker)
                if self.board[y][x] is BoardCell.sp_checker:
                    self.painter.drawPixmap(rect, black_checker)

    def mousePressEvent(self, mouse_event):
        x, y = mouse_event.x() // 50, mouse_event.y() // 50
        if x < self.board_size and y < self.board_size \
                and self.checkers_type is not None:

            if self.checkers_type == BoardCell.fp_checker and y == 0:
                return

            if self.checkers_type == BoardCell.sp_checker \
                    and y == self.board_size - 1:
                return

            self.board[y][x] = self.checkers_type \
                if self.board[y][x] is BoardCell.empty \
                else BoardCell.empty

            self.is_saved = False
            self.update()

    def save_file(self):
        file_name = QFileDialog.getSaveFileName(self, 'Save Config',
                                                'my_config.txt',
                                                filter='Text files (*.txt)')[0]
        try:
            with open(file_name, 'w') as file:
                text = str(self)
                file.write(text)
            self.is_saved = True
        except FileNotFoundError:
            pass

    def closeEvent(self, event):
        if not self.is_saved:
            reply = QMessageBox.question(self, 'Exit',
                                         "Are you sure to exit without save?",
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)

            event.accept() if reply == QMessageBox.Yes else event.ignore()

    def __str__(self):
        string = ''
        for y in range(self.board_size):
            for x in range(self.board_size):
                string += str(int(self.board[y][x]))
            string += '\n'
        return string


def create():
    app = QApplication(sys.argv)
    config = Config()
    config.show()
    sys.exit(app.exec())
