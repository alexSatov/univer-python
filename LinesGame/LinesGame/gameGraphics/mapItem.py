from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtCore import QRectF


class MapItem(QGraphicsItem):
    def __init__(self, x, y, field_visualizer):
        super().__init__()
        self.field_visualizer = field_visualizer
        self.background_pixmap = self.field_visualizer.tile_pixmap
        self.size = field_visualizer.item_size
        self.x = x * self.size.width()
        self.y = y * self.size.height()
        self.setFlag(QGraphicsItem.ItemIsSelectable)

    def boundingRect(self):
        return QRectF(self.x, self.y, self.size.width(), self.size.height())

    def paint(self, painter, style, widget=None):
        painter.drawPixmap(self.x, self.y, self.size.width(),
                           self.size.height(), self.background_pixmap)

        field_coord = self.get_field_coord()
        ball_pixmap = self.field_visualizer.get_ball_pixmap(*field_coord)

        if ball_pixmap is not None:
            painter.drawPixmap(self.x, self.y, self.size.width(),
                               self.size.height(), ball_pixmap)

    def get_field_coord(self):
        return self.x // self.size.width(), self.y // self.size.height()
