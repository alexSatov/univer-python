import sys
import argparse
from png import PngInfo
from graphic import MainWindow
from PyQt5.QtWidgets import QApplication


def try_start_console_mode():
    info = 'PNG Decoder. Check README for detailed information'
    parser = argparse.ArgumentParser(description=info)

    parser.add_argument('-f', '--file', type=str,
                        help='print png file info into console')

    args = parser.parse_args()
    return args.file


if __name__ == '__main__':
    filename = try_start_console_mode()

    if filename:
        try:
            print(PngInfo(filename))
        except AttributeError as e:
            print(e.args[0])
        exit()

    app = QApplication(sys.argv)
    png_parser_window = MainWindow()
    sys.exit(app.exec())
