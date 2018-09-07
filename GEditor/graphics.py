from enum import IntEnum
from resolution import ImageResolutionWindow
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QPixmap, QIcon, QPainter, QImage, QPen, QBrush
from PyQt5.QtWidgets import QWidget, QMessageBox, QMainWindow, QScrollArea, \
    QAction, QLabel, QFileDialog, QVBoxLayout, QGridLayout, QPushButton, \
    QColorDialog, QComboBox


class Tool(IntEnum):
    pen = 0
    brush = 1
    eraser = 2
    line = 3
    rect = 4
    ellipse = 5
    f_rect = 6
    f_ellipse = 7


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.saved = False
        self.setGeometry(350, 150, 1000, 700)
        self.main_widget = MainWidget(self)
        self.resolution_window = None
        self.setCentralWidget(self.main_widget)
        self.init_ui()

    def init_ui(self):
        creating = QAction('Create', self)
        creating.setShortcut('Ctrl+N')
        creating.triggered.connect(self.create_image)

        opening = QAction('Open', self)
        opening.setShortcut('Ctrl+O')
        opening.triggered.connect(self.open_image)

        saving = QAction('Save', self)
        saving.setShortcut('Ctrl+S')
        saving.triggered.connect(self.save_image)

        undo = QAction('Undo', self)
        undo.setShortcut('Ctrl+Z')
        undo.triggered.connect(self.undo)

        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(creating)
        file_menu.addAction(saving)
        file_menu.addAction(opening)

        edit_menu = menu_bar.addMenu('&Edit')
        edit_menu.addAction(undo)

        self.setWindowTitle('Graphic editor')
        self.setWindowIcon(QIcon('logo.png'))
        self.show()

    def save_image(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, 'Сохранить', filter='Images (*.png *.jpg *.jpeg *.bmp)')
        if file_name != "":
            self.main_widget.drawing_area.drawing_field.image.save(file_name)
            self.main_widget.drawing_area.drawing_field.states = []
            self.saved = True

    def open_image(self):
        field = self.main_widget.drawing_area.drawing_field

        file_name, _ = QFileDialog.getOpenFileName(
            self, 'Открыть', filter='Images (*.png *.jpg *.jpeg *.bmp)')

        if file_name != "":
            field.image = QImage(file_name)
            field.update()

    def undo(self):
        field = self.main_widget.drawing_area.drawing_field
        if field.states:
            field.image = field.states.pop()
            field.update()

    def create_image(self):
        self.resolution_window = ImageResolutionWindow(self)

    def closeEvent(self, event):
        if not self.saved:
            reply = QMessageBox.question(self, 'Exit',
                                         "Вы хотите выйти без сохранения?",
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)

            event.accept() if reply == QMessageBox.Yes else event.ignore()


class MainWidget(QWidget):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.drawing_area = DrawingArea(self)
        self.toolbar = ToolBar(self)
        self.init_ui()

    def init_ui(self):
        main_vlayout = QVBoxLayout()
        main_vlayout.addWidget(self.toolbar)
        main_vlayout.addWidget(self.drawing_area)
        self.setLayout(main_vlayout)


class ThicknessSelect(QComboBox):
    def __init__(self, toolbar):
        super().__init__(toolbar)
        self.main_widget = toolbar.main_widget
        self.addItem('1')
        self.addItem('2')
        self.addItem('3')
        self.addItem('4')
        self.setFixedWidth(60)
        self.currentTextChanged.connect(self.change_thickness)

    def change_thickness(self, item_value):
        self.main_widget.drawing_area.drawing_field.thickness = int(item_value)


class ToolBar(QWidget):
    def __init__(self, main_widget):
        super().__init__(main_widget)
        self.main_widget = main_widget
        self.color_label = QLabel()
        self.color_label.setAlignment(Qt.AlignCenter)
        self.set_color_label(self.main_widget.drawing_area.drawing_field.color)
        self.init_ui()

    def init_ui(self):
        grid = QGridLayout()

        self.add_tools_to_grid(grid)
        self.add_color_to_grid(grid)
        self.add_figures_to_grid(grid)
        self.add_thickness_to_grid(grid)

        self.setLayout(grid)

    def add_tools_to_grid(self, grid):
        pen = QPushButton(QIcon('tools/pen'), 'Pen', self)
        pen.clicked.connect(self.set_pen)

        brush = QPushButton(QIcon('tools/brush'), 'Brush', self)
        brush.clicked.connect(self.set_brush)

        eraser = QPushButton(QIcon('tools/eraser'), 'Eraser', self)
        eraser.clicked.connect(self.set_eraser)

        tools_label = QLabel()
        tools_label.setAlignment(Qt.AlignCenter)
        tools_label.setText('Инструменты')

        grid.addWidget(pen, 0, 0)
        grid.addWidget(brush, 0, 1)
        grid.addWidget(eraser, 0, 2)
        grid.addWidget(tools_label, 2, 0, 2, 3)

    def add_figures_to_grid(self, grid):
        line = QPushButton(QIcon('figures/line'), 'Line', self)
        line.clicked.connect(self.set_line)

        rect = QPushButton(QIcon('figures/rect'), 'Rect', self)
        rect.clicked.connect(self.set_rect)

        ellipse = QPushButton(QIcon('figures/ellipse'), 'Ellipse', self)
        ellipse.clicked.connect(self.set_ellipse)

        f_rect = QPushButton(QIcon('figures/f_rect'), 'FRect', self)
        f_rect.clicked.connect(self.set_f_rect)

        f_ellipse = QPushButton(QIcon('figures/f_ellipse'), 'FEllipse', self)
        f_ellipse.clicked.connect(self.set_f_ellipse)

        figures_label = QLabel()
        figures_label.setAlignment(Qt.AlignCenter)
        figures_label.setText('Фигуры')

        grid.addWidget(rect, 0, 3)
        grid.addWidget(ellipse, 0, 4)
        grid.addWidget(line, 0, 5)
        grid.addWidget(f_rect, 1, 3)
        grid.addWidget(f_ellipse, 1, 4)
        grid.addWidget(figures_label, 2, 2, 2, 5)

    def add_thickness_to_grid(self, grid):
        thickness_select = ThicknessSelect(self)

        thickness_label = QLabel()
        thickness_label.setAlignment(Qt.AlignCenter)
        thickness_label.setText('Толщина')

        grid.addWidget(thickness_select, 0, 6, alignment=Qt.AlignCenter)
        grid.addWidget(thickness_label, 2, 6)

    def add_color_to_grid(self, grid):
        color_label_name = QLabel()
        color_label_name.setAlignment(Qt.AlignCenter)
        color_label_name.setText('Цвет')

        color_select = QPushButton(QIcon('tools/color_select'), '', self)
        color_select.clicked.connect(self.select_color)

        color_change_label = QLabel()
        color_change_label.setAlignment(Qt.AlignCenter)
        color_change_label.setText('Выбор цвета')

        grid.addWidget(self.color_label, 0, 7)
        grid.addWidget(color_label_name, 2, 7)
        grid.addWidget(color_select, 0, 8)
        grid.addWidget(color_change_label, 2, 8)

    def select_color(self):
        color = QColorDialog.getColor()
        self.main_widget.drawing_area.drawing_field.color = color
        self.set_color_label(color)

    def set_pen(self):
        self.main_widget.drawing_area.drawing_field.tool = Tool.pen

    def set_brush(self):
        self.main_widget.drawing_area.drawing_field.tool = Tool.brush

    def set_eraser(self):
        self.main_widget.drawing_area.drawing_field.tool = Tool.eraser

    def set_line(self):
        self.main_widget.drawing_area.drawing_field.tool = Tool.line

    def set_rect(self):
        self.main_widget.drawing_area.drawing_field.tool = Tool.rect

    def set_ellipse(self):
        self.main_widget.drawing_area.drawing_field.tool = Tool.ellipse

    def set_f_rect(self):
        self.main_widget.drawing_area.drawing_field.tool = Tool.f_rect

    def set_f_ellipse(self):
        self.main_widget.drawing_area.drawing_field.tool = Tool.f_ellipse

    def set_color_label(self, color):
        image = QImage(30, 30, QImage.Format_ARGB32)
        painter = QPainter(image)
        painter.begin(self)
        painter.setPen(QPen(color))
        painter.setBrush(QBrush(color))
        painter.drawRect(0, 0, 30, 30)
        painter.end()
        self.color_label.setPixmap(QPixmap(image))


class DrawingArea(QScrollArea):
    def __init__(self, main_widget):
        super().__init__(main_widget)
        self.main_widget = main_widget
        self.drawing_field = DrawingField(self)
        self.init_ui()

    def init_ui(self):
        self.setWidgetResizable(True)
        self.setWidget(self.drawing_field)


class DrawingField(QLabel):
    def __init__(self, drawing_area):
        super().__init__(drawing_area)
        self.tools = {
            Tool.pen: self.draw_pen_line,
            Tool.brush: self.draw_brush_line,
            Tool.eraser: self.draw_eraser_line,
            Tool.line: self.draw_line,
            Tool.rect: self.draw_rect,
            Tool.ellipse: self.draw_ellipse,
            Tool.f_rect: self.draw_f_rect,
            Tool.f_ellipse: self.draw_f_ellipse
        }

        self.states = []
        self.tool = Tool.pen
        self.color = Qt.black
        self.thickness = 1
        self.image = QImage(800, 500, QImage.Format_ARGB32)
        self.pen = QPen(Qt.black, 1)
        self.drawing_point = None
        self.init_ui()

    def init_ui(self):
        self.image.fill(Qt.white)
        self.setAlignment(Qt.AlignLeading)
        self.update()

    def update(self):
        self.setPixmap(QPixmap(self.image))

    def mousePressEvent(self, mouse_event):
        self.drawing_point = QPoint(mouse_event.x(), mouse_event.y())
        self.states.append(self.image.copy())

    def mouseMoveEvent(self, mouse_event):
        if self.drawing_point:
            current_point = QPoint(mouse_event.x(), mouse_event.y())
            self.tools[self.tool](current_point)
            self.update()

    def mouseReleaseEvent(self, mouse_event):
        if self.drawing_point:
            current_point = QPoint(mouse_event.x(), mouse_event.y())
            self.tools[self.tool](current_point)
            self.drawing_point = None
            self.update()

    def draw_pen_line(self, current_point):
        painter = QPainter(self.image)
        painter.setPen(QPen(self.color, self.thickness))
        painter.drawLine(self.drawing_point, current_point)
        self.drawing_point = current_point

    def draw_brush_line(self, current_point):
        painter = QPainter(self.image)
        painter.setPen(QPen(self.color))
        painter.setBrush(QBrush(self.color))
        painter.drawEllipse(
            current_point, self.thickness*2, self.thickness*2)
        self.drawing_point = current_point

    def draw_eraser_line(self, current_point):
        painter = QPainter(self.image)
        painter.setPen(QPen(Qt.white, self.thickness*5))
        painter.drawLine(self.drawing_point, current_point)
        self.drawing_point = current_point

    def painter_for_figure(self):
        self.image = self.states.pop()
        self.states.append(self.image.copy())
        painter = QPainter(self.image)
        painter.setPen(QPen(self.color, self.thickness))
        return painter

    def draw_line(self, current_point):
        painter = self.painter_for_figure()
        painter.drawLine(self.drawing_point, current_point)

    def draw_rect(self, current_point):
        painter = self.painter_for_figure()
        rect = self.rect_from_two_points(self.drawing_point, current_point)
        painter.drawRect(rect)

    def draw_ellipse(self, current_point):
        painter = self.painter_for_figure()
        ellipse = self.rect_from_two_points(self.drawing_point, current_point)
        painter.drawEllipse(ellipse)

    def painter_for_filled_figure(self):
        painter = self.painter_for_figure()
        painter.setPen(QPen(self.color, 1))
        painter.setBrush(QBrush(self.color))
        return painter

    def draw_f_rect(self, current_point):
        painter = self.painter_for_filled_figure()
        rect = self.rect_from_two_points(self.drawing_point, current_point)
        painter.drawRect(rect)

    def draw_f_ellipse(self, current_point):
        painter = self.painter_for_filled_figure()
        ellipse = self.rect_from_two_points(self.drawing_point, current_point)
        painter.drawEllipse(ellipse)

    @staticmethod
    def rect_from_two_points(p1, p2):
        x = min(p1.x(), p2.x())
        y = min(p1.y(), p2.y())
        width = abs(p1.x() - p2.x())
        height = abs(p1.y() - p2.y())
        return QRect(x, y, width, height)
