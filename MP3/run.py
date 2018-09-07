import sys
import argparse
from mp3 import Mp3Info
from graphics import MainWindow
from PyQt5.QtWidgets import QApplication


def try_start_console_mode():
    info = 'MP3 Decoder. Check README for detailed information'
    parser = argparse.ArgumentParser(description=info)

    parser.add_argument('-f', '--file', type=str,
                        help='print mp3 file info into console')

    args = parser.parse_args()
    return args.file


if __name__ == '__main__':
    filename = try_start_console_mode()

    if filename:
        try:
            print(Mp3Info(filename))
        except AttributeError as e:
            print(e.args[0])
        exit()

    app = QApplication(sys.argv)
    png_parser_window = MainWindow()
    sys.exit(app.exec())
