import os
from mp3 import Mp3Info

from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import Qt, QUrl, QSize, QThread
from PyQt5.QtGui import QIcon, QPalette
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QScrollArea, QAction, \
    QLabel, QFileDialog, QVBoxLayout, QHBoxLayout, QWidget, QListWidget, \
    QPushButton, QSlider, QAbstractItemView, QTableWidget, QTableWidgetItem


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
        opening.triggered.connect(self.main_widget.request_mp3_file)

        menu_bar = self.menuBar()
        file_open = menu_bar.addMenu('&Open')
        file_open.addAction(opening)

        self.setWindowTitle('MP3')
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
        self.track_name = TrackName(self)
        self.player_window = PlayerWindow(self)
        self.mp3_info_window = Mp3InfoWindow(self)
        self.current_file_screen = CurrentFileScreen(self)
        self.hex_table = HexTable(self)
        self.byte_info_screen = ByteInfoScreen(self)
        self.init_ui()

    def init_ui(self):
        main_vlayout = QVBoxLayout()
        main_hlayout = QHBoxLayout()

        v1_layout = QVBoxLayout()
        v1_layout.addWidget(self.track_name)
        v1_layout.addWidget(self.player_window)
        v1_layout.addWidget(self.mp3_info_window)

        v2_layout = QVBoxLayout()
        v2_layout.addWidget(self.byte_info_screen)
        v2_layout.addWidget(self.hex_table)

        main_hlayout.addLayout(v1_layout)
        main_hlayout.addLayout(v2_layout)

        main_vlayout.addLayout(main_hlayout)
        main_vlayout.addWidget(self.current_file_screen)
        self.setLayout(main_vlayout)

    def request_mp3_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open File',
                                                   filter='MP3 Music (*.mp3)')
        self.open_mp3_file(file_name)

    def open_mp3_file(self, file_name):
        if file_name == '':
            return

        cur_dir = os.path.dirname(file_name)
        prev_dir = os.path.dirname(self.current_file) if \
            self.current_file is not None else None

        self.current_file = file_name
        self.current_file_screen.update()
        self.player_window.stop()
        self.mp3_info_window.mp3_info_list.clear()
        if not cur_dir == prev_dir:
            self.player_window.set_list_of_all_mp3_files_in_current_dir()

        if self.hex_table.filler is not None and \
                self.hex_table.filler.isRunning():
            self.hex_table.filler.terminate()

        try:
            self.track_name.update()
            self.mp3_info_window.update()
            self.hex_table.create_table()
        except AttributeError as e:
            self.mp3_info_window.mp3_info_list.addItem(e.args[0])

    def get_mp3_info(self):
        return self.mp3_info_window.mp3_info


class ByteInfoScreen(QLabel):
    def __init__(self, main_widget):
        super().__init__(main_widget)
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
    def __init__(self, main_widget):
        super().__init__(main_widget)
        self.main_widget = main_widget
        self.mp3_info = None
        self.filler = None
        self.table = QTableWidget()
        self.setWidgetResizable(True)
        self.setWidget(self.table)

    def create_table(self):
        self.mp3_info = self.main_widget.get_mp3_info()
        self.filler = TableFiller(self.fill_table)
        self.filler.start()

        self.table.cellClicked.connect(self.write_byte_info)

    def fill_table(self):
        with open(self.mp3_info.filename, 'rb') as file:
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

    def write_byte_info(self, row, column):
        self.main_widget.byte_info_screen.update('{}, {}'.format(row, column))


class TrackName(QLabel):
    def __init__(self, main_widget):
        super().__init__(main_widget)
        self.main_widget = main_widget
        self.setAlignment(Qt.AlignCenter)

    def update(self):
        filename = '' if self.main_widget.current_file is None else \
            os.path.basename(self.main_widget.current_file)[:-4]
        self.setText(filename)


class PlayerWindow(QWidget):
    def __init__(self, main_widget):
        super().__init__(main_widget)
        self.main_widget = main_widget
        self.mp3_files = []
        self.played = False
        self.is_pause = False
        self.player = QMediaPlayer()
        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.init_ui()

    def init_ui(self):
        previous_file = QPushButton(QIcon('pictures/prev.png'), '', self)
        previous_file.setFixedSize(56, 34)
        previous_file.setIconSize(QSize(40, 24))

        rewind = QPushButton(QIcon('pictures/rewind.png'), '', self)
        rewind.setFixedSize(56, 34)
        rewind.setIconSize(QSize(40, 24))

        play = QPushButton(QIcon('pictures/play.png'), '', self)
        play.setFixedSize(56, 34)
        play.setIconSize(QSize(40, 24))

        forward = QPushButton(QIcon('pictures/forward.png'), '', self)
        forward.setFixedSize(56, 34)
        forward.setIconSize(QSize(40, 24))

        next_file = QPushButton(QIcon('pictures/next.png'), '', self)
        next_file.setFixedSize(56, 34)
        next_file.setIconSize(QSize(40, 24))

        previous_file.clicked.connect(self.open_previous_file)
        play.clicked.connect(self.play_or_pause)
        next_file.clicked.connect(self.open_next_file)

        volume_slider = QSlider(Qt.Horizontal)
        volume_slider.setFixedWidth(100)
        volume_slider.setValue(50)
        volume_slider.valueChanged.connect(self.change_volume)

        self.layout.addWidget(previous_file)
        self.layout.addWidget(rewind)
        self.layout.addWidget(play)
        self.layout.addWidget(forward)
        self.layout.addWidget(next_file)
        self.layout.addWidget(volume_slider)

        self.setLayout(self.layout)

    def change_volume(self, volume):
        self.player.setVolume(volume)

    def play_or_pause(self):
        if self.is_pause:
            self.play()
        elif not self.played:
            self.start_play()
        else:
            self.pause()

    def play(self):
        self.player.play()
        self.played = True
        self.is_pause = False

    def pause(self):
        self.player.pause()
        self.is_pause = True

    def stop(self):
        self.player.stop()
        self.played = False
        self.is_pause = False

    def start_play(self):
        file = self.main_widget.current_file
        if file is not None:
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(file)))
            self.played = True
            self.play()

    def open_next_file(self):
        if self.played:
            self.stop()

        if self.main_widget.current_file is not None:
            cur_file_index = self.mp3_files.index(self.main_widget.current_file)

            if cur_file_index == len(self.mp3_files) - 1:
                cur_file_index = -1

            self.main_widget.open_mp3_file(self.mp3_files[cur_file_index + 1])

    def open_previous_file(self):
        if self.played:
            self.stop()

        if self.main_widget.current_file is not None:
            cur_file_index = self.mp3_files.index(self.main_widget.current_file)
            self.main_widget.open_mp3_file(self.mp3_files[cur_file_index - 1])

    def set_list_of_all_mp3_files_in_current_dir(self):
        current_file = self.main_widget.current_file
        current_dir = os.path.dirname(current_file)
        all_files = os.listdir(current_dir)
        self.mp3_files = [current_dir + '/' + file for file in all_files
                          if file[-4:] == '.mp3']


class Mp3InfoWindow(QScrollArea):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.mp3_info = None
        self.mp3_info_list = QListWidget()
        self.setBackgroundRole(QPalette.Light)
        self.update()
        self.setWidgetResizable(True)
        self.setWidget(self.mp3_info_list)

    def update(self):
        if self.main_window.current_file is not None:
            self.mp3_info = Mp3Info(self.main_window.current_file)
            self.mp3_info_list.addItems(str(self.mp3_info).split('\n'))


class CurrentFileScreen(QLabel):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.update()

    def update(self, *__args):
        text = 'File path: {}'.format(self.main_window.current_file)
        self.setToolTip(text)
        self.setText(text)
