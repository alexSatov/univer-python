import os
from math import floor
from time import sleep
from png import PngInfo, int_from_bytes
from zlib import decompress

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon, QPalette, QImage, QColor, QRgba64
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QScrollArea, QAction, \
    QLabel, QFileDialog, QVBoxLayout, QHBoxLayout, QWidget, QListWidget, \
    QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView


class MainWindow(QMainWindow):
    def __init__(self, file_name=None):
        super().__init__()
        self.setMinimumSize(850, 550)
        self.main_widget = MainWidget(self, file_name)
        self.setCentralWidget(self.main_widget)
        self.init_ui()

    def init_ui(self):
        opening = QAction('Open', self)
        opening.setShortcut('Ctrl+O')
        opening.triggered.connect(self.main_widget.request_image_file)

        menu_bar = self.menuBar()
        file_open = menu_bar.addMenu('&Open')
        file_open.addAction(opening)

        self.setWindowTitle('PNG')
        self.setWindowIcon(QIcon('logo.png'))
        self.show()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Exit', "Are you sure to exit?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        event.accept() if reply == QMessageBox.Yes else event.ignore()


class MainWidget(QWidget):
    def __init__(self, main_window, file_name):
        super().__init__(main_window)
        self.main_window = main_window
        self.current_file = os.path.abspath(file_name) if \
            file_name is not None else None
        self.image_info_window = ImageInfoWindow(self)
        self.image_window = ImageWindow(self)
        self.current_file_screen = CurrentFileScreen(self)
        self.file_switcher = FileSwitcher(self)
        self.hex_table = HexTable(self)
        self.byte_info_screen = ByteInfoScreen(self)
        self.init_ui()

    def init_ui(self):
        main_vlayout = QVBoxLayout()
        main_hlayout = QHBoxLayout()

        v1_layout = QVBoxLayout()
        v1_layout.addWidget(self.image_window)
        v1_layout.addWidget(self.image_info_window)

        v2_layout = QVBoxLayout()
        v2_layout.addWidget(self.byte_info_screen)
        v2_layout.addWidget(self.hex_table)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.current_file_screen)
        hlayout.addWidget(self.file_switcher)

        main_hlayout.addLayout(v1_layout)
        main_hlayout.addLayout(v2_layout)

        main_vlayout.addLayout(main_hlayout)
        main_vlayout.addLayout(hlayout)
        self.setLayout(main_vlayout)

    def request_image_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open File',
                                                   filter='PNG images (*.png)')
        self.open_image_file(file_name)

    def open_image_file(self, file_name):
        if file_name == '':
            return

        self.current_file = file_name
        self.current_file_screen.update()
        self.image_info_window.image_info_list.clear()

        if self.image_window.filler is not None and \
                self.image_window.filler.isRunning():
            self.image_window.filler.terminate()

        self.image_window.image = QImage()
        self.image_window.image_label.clear()

        try:
            self.image_info_window.update()
            # self.hex_table.create_table()
            self.image_window.draw_image(self.current_file)
        except AttributeError as e:
            self.image_info_window.image_info_list.addItem(e.args[0])
            self.image_window.image_label.setPixmap(QPixmap())

    def get_image_info(self):
        return self.image_info_window.image_info


class ByteInfoScreen(QLabel):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.setFixedHeight(40)

    def update(self, text):
        self.setText(text)


class TableFiller(QThread):
    def __init__(self, fill_table):
        super().__init__()
        self.fill_table = fill_table

    def run(self):
        self.fill_table()


class HexTable(QScrollArea):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.image_info = None
        self.table = QTableWidget()
        self.setWidgetResizable(True)
        self.setWidget(self.table)

    def create_table(self):
        self.image_info = self.main_window.get_image_info()

        with open(self.image_info.file_name, 'rb') as file:
            byte_count = len(file.read())
            file.seek(0)
            row_count = byte_count // 16 + 1

            self.table.setRowCount(row_count)
            self.table.setColumnCount(16)
            self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            for row in range(row_count):
                for column in range(16):
                    item = QTableWidgetItem()
                    text = file.read(1).hex()
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setText(text)
                    self.table.setItem(row, column, item)

        self.table.cellClicked.connect(self.write_byte_info)

    def write_byte_info(self, row, column):
        self.main_window.byte_info_screen.update('{}, {}'.format(row, column))


class ImageFiller(QThread):
    def __init__(self, fill_image):
        super().__init__()
        self.fill_image = fill_image

    def run(self):
        self.fill_image()


class ImageWindow(QScrollArea):
    update_image_signal = pyqtSignal()

    def __init__(self, main_window):
        super().__init__(main_window)
        self.filter_method = {0: self.none,
                              1: self.sub,
                              2: self.up,
                              3: self.average,
                              4: self.paeth}

        self.drawing_method = {0: self.draw_g_pixel,
                               2: self.draw_rgb_pixel,
                               3: self.draw_palette_pixel,
                               4: self.draw_ga_pixel,
                               6: self.draw_rgba_pixel}

        self.image = None
        self.pixmap = None
        self.filler = None
        self.image_info = None
        self.image_label = QLabel()
        self.main_window = main_window
        self.update_image_signal.connect(self.update)
        self.init_ui()

    def init_ui(self):
        self.image_label.setAlignment(Qt.AlignCenter)
        self.draw_image(self.main_window.current_file)
        self.setWidgetResizable(True)
        self.setWidget(self.image_label)

    def update(self):
        self.pixmap = QPixmap(self.image)
        self.image_label.setPixmap(self.pixmap)

    def draw_image(self, image_name):
        if image_name is not None:
            self.image_info = self.main_window.get_image_info()
            self.image = QImage(self.image_info.info['Width'],
                                self.image_info.info['Height'],
                                QImage.Format_ARGB32)
            self.filler = ImageFiller(self.fill_image)
            self.filler.start()

    def fill_image(self):
        try:
            color_type = int(self.image_info.info['Color type'][0])
            # self.check_background_color(color_type)
            bpp = self.get_bpp()
            scanlines = self.get_scanlines(self.image_info.info['Width'], bpp)
            pixlines = self.cancel_filter_method(scanlines, bpp)
            self.draw_pixels(self.drawing_method[color_type], pixlines, bpp)
        except IndexError:
            print('Unsupported image')

    # def check_background_color(self, color_type):
    #     if 'Background color' in self.image_info.info.keys():
    #         color = None
    #         entry = self.image_info.info['Background color']
    #         if color_type == 3:
    #             _, str_index = entry.split(':')
    #             color = self.get_palette_color(int(str_index))
    #             color = QColor(*color).rgba()
    #         if color_type in (2, 6):
    #             _, str_red, str_green, str_blue, _ = entry.split('\n')
    #             _, red = str_red.split(':')
    #             _, green = str_green.split(':')
    #             _, blue = str_blue.split(':')
    #             color = (int(red), int(green), int(blue), 65535)
    #             color = QRgba64.fromRgba64(*color).toArgb32()
    #         if color_type in (0, 4):
    #             _, gray = entry.split(':')
    #             color = (int(gray), int(gray), int(gray), 65535)
    #             color = QRgba64.fromRgba64(*color).toArgb32()
    #         self.image.fill(QColor(color))

    def draw_pixels(self, drawing_method, pixlines, bpp):
        if pixlines is not None:
            lines_count = len(pixlines)
            pixels_count = self.image_info.info['Width']

            for y in range(lines_count):
                pixline = pixlines[y]
                for x in range(pixels_count):
                    pixel = pixline[bpp*x:bpp*(x+1)]
                    drawing_method(pixel, x, y)
                self.update_image_signal.emit()
                sleep(0.00001)

    def draw_rgb_pixel(self, pixel, x, y):
        sample_len = len(pixel) // 3
        red = int_from_bytes(pixel[0:sample_len])
        green = int_from_bytes(pixel[sample_len:sample_len*2])
        blue = int_from_bytes(pixel[sample_len*2:sample_len*3])
        color = QRgba64.fromRgba64(red, green, blue, 65535).toArgb32() \
            if sample_len == 2 else QColor(red, green, blue).rgba()
        self.image.setPixel(x, y, color)

    def draw_rgba_pixel(self, pixel, x, y):
        sample_len = (len(pixel) - 1) // 3
        red = int_from_bytes(pixel[0:sample_len])
        green = int_from_bytes(pixel[sample_len:sample_len * 2])
        blue = int_from_bytes(pixel[sample_len * 2:sample_len * 3])
        alpha = int_from_bytes(pixel[sample_len * 3:sample_len * 4])
        color = QRgba64.fromRgba64(red, green, blue, alpha).toArgb32() \
            if sample_len == 2 else QColor(red, green, blue, alpha).rgba()
        self.image.setPixel(x, y, color)

    def draw_g_pixel(self, pixel, x, y):
        sample_len = len(pixel)
        gray = int_from_bytes(pixel)
        color = QRgba64.fromRgba64(gray, gray, gray, 65535).toArgb32()\
            if sample_len == 2 else QColor(gray, gray, gray).rgba()
        self.image.setPixel(x, y, color)

    def draw_ga_pixel(self, pixel, x, y):
        sample_len = len(pixel)
        gray = int_from_bytes(pixel[0:sample_len])
        alpha = int_from_bytes(pixel[sample_len:sample_len*2])
        color = QRgba64.fromRgba64(gray, gray, gray, alpha).toArgb32() \
            if sample_len == 2 else QColor(gray, gray, gray, alpha).rgba()
        self.image.setPixel(x, y, color)

    def draw_palette_pixel(self, pixel, x, y):
        index = int_from_bytes(pixel)
        color = self.get_palette_color(index)
        self.image.setPixel(x, y, QColor(*color).rgba())

    def get_palette_color(self, index):
        color = self.image_info.chunks['PLTE'][index*3:index*3 + 3]
        red, green, blue = color[0], color[1], color[2]
        return red, green, blue

    def cancel_filter_method(self, scanlines, bpp):
        try:
            pixlines = []
            prev_line = None
            for line in scanlines:
                filter_type = line[0]  # First byte is filter id
                pixline = self.filter_method[filter_type](prev_line,
                                                          line[1:], bpp)
                pixlines.append(pixline)
                prev_line = pixline
            return pixlines
        except KeyError:
            print('Unsupported image')

    @staticmethod
    def none(prev_line, line, bpp):
        return line

    @staticmethod
    def sub(prev_line, line, bpp):
        pixline = b''
        for i in range(len(line)):
            left_byte = 0 if i - bpp < 0 else pixline[i - bpp]
            byte = line[i]
            real_byte = (byte + left_byte) % 256
            pixline += real_byte.to_bytes(1, byteorder='big')
        return pixline

    @staticmethod
    def up(prev_line, line, bpp):
        pixline = b''
        for i in range(len(line)):
            upper_byte = prev_line[i] if prev_line is not None else 0
            byte = line[i]
            real_byte = (byte + upper_byte) % 256
            pixline += real_byte.to_bytes(1, byteorder='big')
        return pixline

    @staticmethod
    def average(prev_line, line, bpp):
        pixline = b''
        for i in range(len(line)):
            left_byte = 0 if i - bpp < 0 else pixline[i - bpp]
            upper_byte = prev_line[i] if prev_line is not None else 0
            byte = line[i]
            real_byte = int((byte + floor(left_byte + upper_byte)/2) % 256)
            pixline += real_byte.to_bytes(1, byteorder='big')
        return pixline

    @staticmethod
    def paeth(prev_line, line, bpp):
        pixline = b''
        for i in range(len(line)):
            left_byte = 0 if i - bpp < 0 else pixline[i - bpp]
            upper_byte = prev_line[i] if prev_line is not None else 0
            upper_left_byte = 0 if i - bpp < 0 or prev_line is None \
                else prev_line[i - bpp]
            byte = line[i]
            predictor = ImageWindow.paeth_predictor(left_byte, upper_byte,
                                                    upper_left_byte)
            real_byte = (byte + predictor) % 256
            pixline += real_byte.to_bytes(1, byteorder='big')
        return pixline

    @staticmethod
    def paeth_predictor(left, above, upper_left):
        p = left + above - upper_left
        p_left = abs(p - left)
        p_above = abs(p - above)
        p_upper_left = abs(p - upper_left)

        if p_left <= p_above and p_left <= p_upper_left:
            return left
        if p_above <= p_upper_left:
            return above
        return upper_left

    def get_scanlines(self, width, bpp):
        compressed_data = self.image_info.chunks['IDAT']
        scanline_len = width * bpp + 1
        scanlines = []

        data = b''
        for byte_line in compressed_data:
            data += byte_line

        data = decompress(data)

        i = 0
        while True:
            entry = data[scanline_len*i:scanline_len*(i+1)]
            if entry == b'':
                break
            scanlines.append(entry)
            i += 1

        return scanlines

    def get_bpp(self):
        bytes_to_sample = 2 if self.image_info.info['Bit depth'] == 16 else 1
        samples_count = 0
        bytes_to_alpha = 1
        is_alpha = False
        color_type = int(self.image_info.info['Color type'][0])

        if color_type in (0, 3, 4):
            samples_count = 1
        if color_type in (2, 6):
            samples_count = 3
        if color_type in (4, 6):
            is_alpha = True

        bpp = bytes_to_sample * samples_count
        bpp += bytes_to_alpha if is_alpha else 0
        return bpp

    # def draw_image(self, image_name):
    #     if image_name is not None:
    #         self.image_label.setPixmap(QPixmap(image_name))


class ImageInfoWindow(QScrollArea):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.image_info = None
        self.image_info_list = QListWidget()
        self.setBackgroundRole(QPalette.Light)
        self.update()
        self.setWidgetResizable(True)
        self.setWidget(self.image_info_list)

    def update(self):
        if self.main_window.current_file is not None:
            self.image_info = PngInfo(self.main_window.current_file)
            self.image_info_list.addItems(str(self.image_info).split('\n'))


class FileSwitcher(QWidget):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        next_file = QPushButton('Next')
        previous_file = QPushButton('Previous')

        next_file.clicked.connect(self.open_next_file)
        previous_file.clicked.connect(self.open_previous_file)

        hbox = QHBoxLayout()
        hbox.setAlignment(Qt.AlignCenter)
        hbox.addWidget(previous_file)
        hbox.addWidget(next_file)

        self.setLayout(hbox)

    def open_next_file(self):
        if self.main_window.current_file is not None:
            png_files = self.get_all_png_files_in_current_dir()
            cur_file_index = png_files.index(self.main_window.current_file)

            if cur_file_index == len(png_files) - 1:
                cur_file_index = -1

            self.main_window.open_image_file(png_files[cur_file_index + 1])

    def open_previous_file(self):
        if self.main_window.current_file is not None:
            png_files = self.get_all_png_files_in_current_dir()
            cur_file_index = png_files.index(self.main_window.current_file)
            self.main_window.open_image_file(png_files[cur_file_index - 1])

    def get_all_png_files_in_current_dir(self):
        current_file = self.main_window.current_file
        current_dir = os.path.dirname(current_file)
        files = os.listdir(current_dir)
        png_files = [current_dir + '/' + file for file in files
                     if file[-4:] == '.png']
        return png_files


class CurrentFileScreen(QLabel):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.update()

    def update(self, *__args):
        text = 'File path: {}'.format(self.main_window.current_file)
        self.setToolTip(text)
        self.setText(text)
