import sys
from math import pow, log1p
from queue import Queue
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QScrollArea, \
    QAction, QLabel, QFileDialog, QVBoxLayout, QGridLayout, QPushButton, \
    QColorDialog, QComboBox, QLineEdit, QErrorMessage, QFontDialog, QTextEdit
from PyQt5.QtGui import QPixmap, QPainter, QImage, QPen, QBrush, QColor, \
    QTransform, QFont


def insert_image(source, target, x1, y1):
    offset_x = -x1 if x1 < 0 else 0
    offset_y = -y1 if y1 < 0 else 0
    x2 = x1 + source.width() - 1
    y2 = y1 + source.height() - 1
    width = source.width() if x2 < target.width() else target.width() - x1
    height = source.height() if y2 < target.height() else target.height() - y1

    for x in range(width - offset_x):
        for y in range(height - offset_y):
            color = source.pixelColor(x + offset_x, y + offset_y)
            target.setPixelColor(x + x1 + offset_x, y + y1 + offset_y, color)


def get_points_around(x, y):
    return [(x - 1, y), (x, y - 1), (x + 1, y), (x, y + 1)]


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(200, 130, 1000, 700)
        self.widget = Widget(self)
        self.setCentralWidget(self.widget)
        self.init_ui()

    def init_ui(self):
        create_action = QAction('Create', self)
        create_action.setShortcut('Ctrl+N')
        create_action.triggered.connect(self.create)

        open_action = QAction('Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open)

        save_action = QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save)

        resize_action = QAction('Resize', self)
        resize_action.setShortcut('Ctrl+R')
        resize_action.triggered.connect(self.resize)

        undo_action = QAction('Undo', self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self.undo)

        self.statusBar()
        menubar = self.menuBar()
        create_menu = menubar.addMenu('&Create')
        create_menu.addAction(create_action)

        open_menu = menubar.addMenu('&Open')
        open_menu.addAction(open_action)

        save_menu = menubar.addMenu('&Save')
        save_menu.addAction(save_action)

        resize_menu = menubar.addMenu('&Resize')
        resize_menu.addAction(resize_action)

        undo_menu = menubar.addMenu('&Undo')
        undo_menu.addAction(undo_action)

        self.setWindowTitle('Graphic Editor')
        self.show()

    def create(self):
        self.new_window = NewWindow(self)

    def resize(self):
        self.new_window = NewWindow(self, False)

    def open(self):
        paint = self.widget.paint_widget.paint
        file, _ = QFileDialog.getOpenFileName(self, 'Открыть',
            filter='Images (*.png *.jpg *.jpeg *.bmp)')
        if file != "":
            paint.image = QImage(file)
            paint.update()

    def save(self):
        file, _ = QFileDialog.getSaveFileName(self, 'Сохранить',
            filter='Images (*.png *.jpg *.jpeg *.bmp)')
        if file != "":
            self.widget.paint_widget.paint.image.save(file)
            self.widget.paint_widget.paint.layers = []
            self.saving = True

    def undo(self):
        paint = self.widget.paint_widget.paint
        paint.unpick()
        if paint.layers:
            paint.image = paint.layers.pop()
            paint.update()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

        if e.key() == Qt.Key_Delete:
            self.widget.paint_widget.paint.apply_filter(Filter.fill, Qt.white)


class NewWindow(QWidget):
    def __init__(self, window, clear=True):
        super().__init__()
        self.clear = clear
        self.window = window
        self.width_line = QLineEdit()
        self.height_line = QLineEdit()
        self.init_ui()

    def init_ui(self):
        grid = QGridLayout()
        image = self.window.widget.paint_widget.paint.image

        width = QLabel()
        width.setAlignment(Qt.AlignRight)
        width.setText('Ширина:')

        height = QLabel()
        height.setAlignment(Qt.AlignRight)
        height.setText('Высота:')

        self.width_line.setInputMask('0000')
        self.width_line.setText(str(image.width()))
        self.height_line.setInputMask('0000')
        self.height_line.setText(str(image.height()))

        ok_button = QPushButton('Ок', self)
        ok_button.clicked.connect(self.create_image)

        grid.addWidget(width, 0, 0)
        grid.addWidget(self.width_line, 0, 1)
        grid.addWidget(height, 1, 0)
        grid.addWidget(self.height_line, 1, 1)
        grid.addWidget(ok_button, 2, 0, alignment=Qt.AlignCenter)

        self.setLayout(grid)
        self.show()

    def create_image(self):
        paint = self.window.widget.paint_widget.paint
        width_str, height_str = self.width_line.text(), self.height_line.text()
        width = 0 if width_str == '' else int(width_str)
        height = 0 if height_str == '' else int(height_str)

        if width == 0 or height == 0:
            error = QErrorMessage(self)
            error.showMessage('Change resolution')
            return

        image = QImage(width, height, QImage.Format_ARGB32)
        image.fill(Qt.white)

        if not self.clear:
            insert_image(paint.image, image, 0, 0)

        paint.image = image
        paint.update()
        self.close()


class Widget(QWidget):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.paint_widget = PaintWidget(self)
        self.make_grid = MakeGrid(self)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.make_grid)
        layout.addWidget(self.paint_widget)
        self.setLayout(layout)


class SelectFat(QComboBox):
    def __init__(self, grid):
        super().__init__(grid)
        self.widget = grid.widget
        self.addItem('1')
        self.addItem('2')
        self.addItem('3')
        self.addItem('4')
        self.setFixedWidth(60)
        self.currentTextChanged.connect(self.change_fat)

    def change_fat(self, item_value):
        self.widget.paint_widget.paint.fat = int(item_value)


class TextDrawer(QWidget):
    def __init__(self, grid):
        super().__init__()
        self.grid = grid
        self.text_edit = QTextEdit()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        draw_text = QPushButton('Draw')
        draw_text.clicked.connect(self.draw_text)

        layout.addWidget(self.text_edit)
        layout.addWidget(draw_text)

        self.setLayout(layout)
        self.show()

    def draw_text(self):
        self.grid.widget.paint_widget.paint.apply_filter(
            Filter.text, self.text_edit.toPlainText())


class Tool:
    pen = 'Pen'
    brush = 'Brush'
    eraser = 'Eraser'
    line = 'Line'
    rect = 'Rect'
    ellipse = 'Ellipse'
    bucket = 'Bucket'
    pick = 'Pick'


class Filter:
    fill = 'Fill'
    text = 'Text'
    grayscale = 'Grayscale'
    autolevels = 'Autolevels'
    reflect_v = 'ReflectV'
    reflect_h = 'ReflectH'
    rotate_left = '90°Left'
    rotate_right = '90°Right'


class MakeGrid(QWidget):
    def __init__(self, widget):
        super().__init__(widget)
        self.widget = widget
        self.color_label = QLabel()
        self.color_label.setAlignment(Qt.AlignCenter)
        self.make_color(self.widget.paint_widget.paint.color)
        self.init_ui()

    def init_ui(self):
        grid = QGridLayout()
        self.buttons(grid)
        self.setLayout(grid)

    def buttons(self, grid):
        pen = QPushButton(Tool.pen)
        brush = QPushButton(Tool.brush)
        eraser = QPushButton(Tool.eraser)
        bucket = QPushButton(Tool.bucket)
        line = QPushButton(Tool.line)
        rect = QPushButton(Tool.rect)
        ellipse = QPushButton(Tool.ellipse)
        pick = QPushButton(Tool.pick)
        color = QPushButton('Colour')
        select_fat = SelectFat(self)
        fill = QPushButton(Filter.fill)
        font = QPushButton('Font')
        text = QPushButton(Filter.text)
        grayscale = QPushButton(Filter.grayscale)
        autolevels = QPushButton(Filter.autolevels)
        reflect_v = QPushButton(Filter.reflect_v)
        reflect_h = QPushButton(Filter.reflect_h)
        rotate_left = QPushButton(Filter.rotate_left)
        rotate_right = QPushButton(Filter.rotate_right)

        pen.clicked.connect(self.make_pen)
        brush.clicked.connect(self.make_brush)
        eraser.clicked.connect(self.make_eraser)
        bucket.clicked.connect(self.make_bucket)
        line.clicked.connect(self.make_line)
        rect.clicked.connect(self.make_rect)
        ellipse.clicked.connect(self.make_ellipse)
        pick.clicked.connect(self.make_pick)
        color.clicked.connect(self.select_color)
        fill.clicked.connect(self.make_fill)
        font.clicked.connect(self.select_font)
        text.clicked.connect(self.make_text)
        grayscale.clicked.connect(self.make_grayscale)
        autolevels.clicked.connect(self.make_autolevels)
        reflect_v.clicked.connect(self.make_reflect_v)
        reflect_h.clicked.connect(self.make_reflect_h)
        rotate_left.clicked.connect(self.make_rotate_left)
        rotate_right.clicked.connect(self.make_rotate_right)

        grid.addWidget(pen, 0, 0)
        grid.addWidget(brush, 0, 1)
        grid.addWidget(eraser, 0, 2)
        grid.addWidget(bucket, 0, 3)
        grid.addWidget(line, 1, 0)
        grid.addWidget(rect, 1, 1)
        grid.addWidget(ellipse, 1, 2)
        grid.addWidget(pick, 1, 3)
        grid.addWidget(color, 0, 4)
        grid.addWidget(self.color_label, 1, 4)
        grid.addWidget(select_fat, 0, 5, alignment=Qt.AlignCenter)
        grid.addWidget(fill, 1, 5, alignment=Qt.AlignCenter)
        grid.addWidget(font, 0, 6)
        grid.addWidget(text, 1, 6)
        grid.addWidget(grayscale, 0, 7)
        grid.addWidget(autolevels, 1, 7)
        grid.addWidget(reflect_v, 0, 8)
        grid.addWidget(reflect_h, 1, 8)
        grid.addWidget(rotate_left, 0, 9)
        grid.addWidget(rotate_right, 1, 9)

    def make_pen(self):
        self.widget.paint_widget.paint.unpick()
        self.widget.paint_widget.paint.tool = Tool.pen

    def make_brush(self):
        self.widget.paint_widget.paint.unpick()
        self.widget.paint_widget.paint.tool = Tool.brush

    def make_eraser(self):
        self.widget.paint_widget.paint.unpick()
        self.widget.paint_widget.paint.tool = Tool.eraser

    def make_bucket(self):
        self.widget.paint_widget.paint.unpick()
        self.widget.paint_widget.paint.tool = Tool.bucket

    def make_line(self):
        self.widget.paint_widget.paint.unpick()
        self.widget.paint_widget.paint.tool = Tool.line

    def make_rect(self):
        self.widget.paint_widget.paint.unpick()
        self.widget.paint_widget.paint.tool = Tool.rect

    def make_ellipse(self):
        self.widget.paint_widget.paint.unpick()
        self.widget.paint_widget.paint.tool = Tool.ellipse

    def make_pick(self):
        self.widget.paint_widget.paint.tool = Tool.pick

    def select_color(self):
        color = QColorDialog.getColor()
        self.widget.paint_widget.paint.color = color
        self.make_color(color)

    def select_font(self):
        font, flag = QFontDialog.getFont()
        self.widget.paint_widget.paint.font = font

    def make_color(self, color):
        image = QImage(30, 30, QImage.Format_ARGB32)
        painter = QPainter(image)
        painter.begin(self)
        painter.setPen(QPen(color))
        painter.setBrush(QBrush(color))
        painter.drawRect(0, 0, 30, 30)
        painter.end()
        self.color_label.setPixmap(QPixmap(image))

    def make_fill(self):
        self.widget.paint_widget.paint.apply_filter(
            Filter.fill, self.widget.paint_widget.paint.color)

    def make_text(self):
        self.text_drawer = TextDrawer(self)

    def make_grayscale(self):
        self.widget.paint_widget.paint.apply_filter(Filter.grayscale)

    def make_autolevels(self):
        self.widget.paint_widget.paint.apply_filter(Filter.autolevels)

    def make_reflect_v(self):
        self.widget.paint_widget.paint.apply_filter(Filter.reflect_v)

    def make_reflect_h(self):
        self.widget.paint_widget.paint.apply_filter(Filter.reflect_h)

    def make_rotate_left(self):
        self.widget.paint_widget.paint.apply_filter(Filter.rotate_left)

    def make_rotate_right(self):
        self.widget.paint_widget.paint.apply_filter(Filter.rotate_right)


class PaintWidget(QScrollArea):
    def __init__(self, widget):
        super().__init__(widget)
        self.widget = widget
        self.paint = Paint(self)
        self.init_ui()

    def init_ui(self):
        self.setWidgetResizable(True)
        self.setWidget(self.paint)


class PickedArea:
    def __init__(self, rect):
        self.rect = rect
        self.origin_rect = rect
        self.image = None
        self.move_point = rect.topLeft()
        self.filtered = False

    def pick_image(self, image):
        if self.rect.width() == 0 or self.rect.height() == 0:
            self.image = QImage()
        else:
            self.image = image.copy(self.rect)

    def move_area_to(self, point):
        a, b = self.move_point, point
        offset_x, offset_y = b.x() - a.x(), b.y() - a.y()
        x, y = self.rect.topLeft().x(), self.rect.topLeft().y()
        w, h = self.rect.width(), self.rect.height()
        top_left = QPoint(x + offset_x, y + offset_y)
        self.rect = QRect(top_left.x(), top_left.y(), w, h)


class Paint(QLabel):
    def __init__(self, paint_widget):
        super().__init__(paint_widget)
        self.tools = {
            Tool.pen: self.pen_drawing,
            Tool.brush: self.brush_drawing,
            Tool.eraser: self.eraser_drawing,
            Tool.bucket: self.bucket_drawing,
            Tool.line: self.line_drawing,
            Tool.rect: self.rect_drawing,
            Tool.ellipse: self.ellipse_drawing,
            Tool.pick: self.pick_drawing
        }

        self.filters = {
            Filter.fill: Paint.fill,
            Filter.text: self.draw_text,
            Filter.grayscale: Paint.to_grayscale,
            Filter.autolevels: Paint.to_full_contrast,
            Filter.reflect_v: Paint.reflect_v,
            Filter.reflect_h: Paint.reflect_h,
            Filter.rotate_left: Paint.rotate_left,
            Filter.rotate_right: Paint.rotate_right
        }

        self.layers = []
        self.tool = Tool.pen
        self.color = Qt.black
        self.font = QFont('Arial', 6)
        self.fat = 1
        self.image = QImage(800, 500, QImage.Format_ARGB32)
        self.pen = QPen(Qt.black, 1)
        self.origin_point = None
        self.picked_area = None
        self.init_ui()

    def init_ui(self):
        self.image.fill(Qt.white)
        self.setAlignment(Qt.AlignLeading)
        self.update()

    def update(self):
        self.setPixmap(QPixmap(self.image))

    def unpick(self):
        if self.picked_area:
            self.picked_area = None
            self.image = self.layers[-1].copy()
            self.update()

    def mousePressEvent(self, event):
        self.origin_point = QPoint(event.x(), event.y())

        if self.tool == Tool.pick and not self.picked_area:
            self.layers.append(self.image.copy())

        if self.picked_area:
            if self.picked_area.rect.contains(self.origin_point):
                self.picked_area.move_point = self.origin_point
                return
            self.unpick()

        self.layers.append(self.image.copy())
        self.tools[self.tool](self.origin_point)
        self.update()

    def mouseMoveEvent(self, event):
        if self.origin_point:
            point = QPoint(event.x(), event.y())
            self.tools[self.tool](point)
            self.update()

    def mouseReleaseEvent(self, event):
        if self.origin_point:
            if self.tool == Tool.pick and not self.picked_area:
                point = QPoint(event.x(), event.y())
                rect = Paint.make_rect_arguments(self.origin_point, point)
                self.picked_area = PickedArea(rect)
                self.picked_area.pick_image(self.layers[-1])
            self.origin_point = None
            self.update()

    def pen_drawing(self, point):
        painter = QPainter(self.image)
        painter.setPen(QPen(self.color, self.fat))
        painter.drawLine(self.origin_point, point)
        self.origin_point = point

    def brush_drawing(self, point):
        painter = QPainter(self.image)
        painter.setPen(QPen(self.color))
        painter.setBrush(QBrush(self.color))
        painter.drawEllipse(point, self.fat * 2, self.fat * 2)
        self.origin_point = point

    def eraser_drawing(self, point):
        painter = QPainter(self.image)
        painter.setPen(QPen(Qt.white, self.fat * 5))
        painter.drawLine(self.origin_point, point)
        self.origin_point = point

    def bucket_drawing(self, point):
        point_x, point_y = point.x(), point.y()
        color = self.image.pixelColor(point_x, point_y)

        if color == self.color:
            return

        self.image.setPixelColor(point_x, point_y, self.color)
        queue = Queue()
        queue.put((point_x, point_y))

        while not queue.empty():
            point_x, point_y = queue.get()
            for x, y in get_points_around(point_x, point_y):
                if self.image.pixelColor(x, y) == color:
                    self.image.setPixelColor(x, y, self.color)
                    queue.put((x, y))

        self.origin_point = None

    def painter_for_figure(self):
        self.image = self.layers[-1].copy()
        painter = QPainter(self.image)
        painter.setPen(QPen(self.color, self.fat))

        return painter

    def line_drawing(self, point):
        painter = self.painter_for_figure()
        painter.drawLine(self.origin_point, point)

    def rect_drawing(self, point):
        painter = self.painter_for_figure()
        rect = self.make_rect_arguments(self.origin_point, point)
        painter.drawRect(rect)

    def ellipse_drawing(self, point):
        painter = self.painter_for_figure()
        ellipse = self.make_rect_arguments(self.origin_point, point)
        painter.drawEllipse(ellipse)

    def pick_drawing(self, point):
        if self.picked_area:
            self.layers.pop()
            painter = self.painter_for_figure()
            painter.setPen(QPen(Qt.white))
            painter.setBrush(QBrush(Qt.white))
            painter.drawRect(self.picked_area.origin_rect)
            self.picked_area.move_area_to(point)
            self.picked_area.move_point = point
            painter.setPen(QPen(Qt.blue, self.fat, Qt.DashLine))
            painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
            rect = self.picked_area.rect
            x, y = rect.topLeft().x(), rect.topLeft().y()
            insert_image(self.picked_area.image, self.image, x, y)
            self.layers.append(self.image.copy())
            painter.drawRect(rect)
        else:
            painter = self.painter_for_figure()
            painter.setPen(QPen(Qt.blue, self.fat, Qt.DashLine))
            rect = self.make_rect_arguments(self.origin_point, point)
            painter.drawRect(rect)

    def apply_filter(self, filter_name, args=None):
        filter = self.filters[filter_name]

        if self.picked_area:
            self.image = self.layers[-1].copy()
            x = self.picked_area.rect.topLeft().x()
            y = self.picked_area.rect.topLeft().y()
            new_image = filter(self.picked_area.image, args) if args else \
                filter(self.picked_area.image)
            self.picked_area.image = new_image

            insert_image(new_image, self.image, x, y)
            self.layers.append(self.image.copy())

            painter = QPainter(self.image)
            painter.setPen(QPen(Qt.blue, self.fat, Qt.DashLine))
            painter.drawRect(self.picked_area.rect)

            self.picked_area.filtered = True
        else:
            self.layers.append(self.image.copy())
            self.image = filter(self.image, args) if args else \
                filter(self.image)

        self.update()

    def draw_text(self, image, text):
        copy = image.copy()
        rect = QRect(0, 0, image.width(), image.height())
        painter = QPainter(copy)
        painter.setFont(self.font)
        painter.setPen(self.color)
        painter.drawText(rect, 0, text)

        return copy

    @staticmethod
    def fill(image, color):
        copy = QImage(image.width(), image.height(), image.format())
        copy.fill(color)

        return copy

    @staticmethod
    def to_grayscale(image):
        copy = image.copy()

        for x in range(image.width()):
            for y in range(image.height()):
                color = image.pixelColor(x, y)
                r, g, b = color.red(), color.green(), color.blue()
                gray = 0.299 * r + 0.587 * g + 0.114 * b
                copy.setPixelColor(x, y, QColor(gray, gray, gray))

        return copy

    @staticmethod
    def to_full_contrast(image):
        center = 128
        average = 0

        for x in range(image.width()):
            for y in range(image.height()):
                color = image.pixelColor(x, y)
                average += color.value()

        average /= image.width() * image.height()

        gamma = 0 if average == 255 else \
            (log1p(center) - log1p(255)) / (log1p(average) - log1p(255))

        copy = Paint.apply_gamma_correction(image, gamma)

        return copy

    @staticmethod
    def reflect_v(image):
        return image.mirrored(False, True)

    @staticmethod
    def reflect_h(image):
        return image.mirrored(True, False)

    @staticmethod
    def rotate_left(image):
        transform = QTransform()
        transform.rotate(-90)
        return image.transformed(transform)

    @staticmethod
    def rotate_right(image):
        transform = QTransform()
        transform.rotate(90)
        return image.transformed(transform)

    @staticmethod
    def apply_gamma_correction(image, gamma=0.5):
        copy = image.copy()
        for x in range(image.width()):
            for y in range(image.height()):
                color = image.pixelColor(x, y)
                h, s, v = color.hue(), color.saturation(), color.value()
                value = pow(v, gamma) * (255 / pow(255, gamma))
                copy.setPixelColor(x, y, QColor.fromHsv(h, s, value))

        return copy

    @staticmethod
    def make_rect_arguments(p1, p2):
        x = min(p1.x(), p2.x())
        y = min(p1.y(), p2.y())
        width = abs(p1.x() - p2.x())
        height = abs(p1.y() - p2.y())
        return QRect(x, y, width, height)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = Window()
    sys.exit(app.exec())
