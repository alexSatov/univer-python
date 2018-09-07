import logging

from PyQt5.QtCore import Qt, QSize, QCoreApplication
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QGraphicsView, QDialog

from gameGraphics.gameOverDialog import GameOverDialog
from gameGraphics.mapItem import MapItem
from gameLogic.gameBalls import Balls


class GameVisualizer(QGraphicsView):
    def __init__(self, parent, scene, sceen_size):
        super().__init__(scene, parent.mainWidget)
        self.screen_size = sceen_size

        self.map_size = 19
        self.scene = scene
        self.game = parent.game
        self.field = self.game.field

        self.item_size = QSize(64, 64)
        self.map_painter = QPainter()

        self.pixmaps = parent.pixmaps
        self.tile_pixmap = self.pixmaps[0]
        self.set_default_state()

    def set_default_state(self):
        self.scene.setBackgroundBrush(Qt.black)
        self.scene.selectionChanged.connect(self.select_item)
        self.init_map()
        self.show()

    def select_item(self):
        selected_items = self.scene.selectedItems()
        for item in selected_items:
            item_location = item.get_field_coord()

            if self.game.is_game_over():
                self.show_game_over_dialog()
                self.scene.update()
                return

            if self.is_ball(*item_location):
                self.game.selected_location = item_location
            else:
                is_path_exist = self.game.is_possible_to_move_ball(*item_location)
                if self.game.selected_location is not None and is_path_exist:
                    self.game.move_ball(*item_location)
                    self.game.next_step()
                    self.scene.update()

    def show_game_over_dialog(self):
        dialog = GameOverDialog(self.game, "You lose", self)
        result = dialog.exec_()

        if result == QDialog.Accepted:
            dialog.close()
            QCoreApplication.instance().quit()
        else:
            self.game.init_start_state()

    def init_map(self):
        self.scene.clear()
        for i in range(self.field.width):
            for j in range(self.field.height):
                new_item = MapItem(j, i, self)
                self.scene.addItem(new_item)
        self.scene.update()

    def get_ball_pixmap(self, x, y):
        item_code = self.field.cells[x][y]
        return self.pixmaps[item_code] if self.is_ball(x, y) else None

    def is_ball(self, x, y):
        item_code = self.field.cells[x][y]
        return item_code in Balls.__members__.values()
