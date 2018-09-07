from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton, \
    QLineEdit, QErrorMessage


class ImageResolutionWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.width_line = QLineEdit()
        self.height_line = QLineEdit()
        self.resolution = None
        self.init_ui()

    def init_ui(self):
        grid = QGridLayout()

        width_label = QLabel()
        width_label.setAlignment(Qt.AlignRight)
        width_label.setText('Ширина:')

        height_label = QLabel()
        height_label.setAlignment(Qt.AlignRight)
        height_label.setText('Высота:')

        self.width_line.setInputMask('0000')
        self.width_line.setText('800')
        self.height_line.setInputMask('0000')
        self.height_line.setText('500')

        ok_button = QPushButton('Ок', self)
        ok_button.clicked.connect(self.create_image)

        cancel_button = QPushButton('Отмена', self)
        cancel_button.clicked.connect(self.close)

        grid.addWidget(width_label, 0, 0)
        grid.addWidget(self.width_line, 0, 1)
        grid.addWidget(height_label, 1, 0)
        grid.addWidget(self.height_line, 1, 1)
        grid.addWidget(ok_button, 2, 0, alignment=Qt.AlignCenter)
        grid.addWidget(cancel_button, 2, 1, alignment=Qt.AlignCenter)

        self.setLayout(grid)
        self.show()

    def create_image(self):
        width_str, height_str = self.width_line.text(), self.height_line.text()
        width = 0 if width_str == '' else int(width_str)
        height = 0 if height_str == '' else int(height_str)

        if width == 0 or height == 0:
            error = QErrorMessage(self)
            error.showMessage('Incorrect resolution')
            return

        image = QImage(width, height, QImage.Format_ARGB32)
        image.fill(Qt.white)

        field = self.main_window.main_widget.drawing_area.drawing_field
        field.image = image
        field.update()
        self.close()
