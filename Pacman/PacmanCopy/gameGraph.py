from PyQt5.QtGui import QPixmap, QPainter, QTransform
from PyQt5.QtWidgets import (QGraphicsScene, QGraphicsItem,
                             QGraphicsView, QLabel, QDialog, QWidget,
                             QInputDialog,
                             QGroupBox, QHBoxLayout)

from PyQt5.QtCore import QTimer, Qt, QRectF, QSize, QCoreApplication
from logic import Direction, directions
import os.path


MAP_ITEMS_PATHS = ["food.png", "wall.png", "empty.png", "gh1.png", "gh2.png",
                   "gh3.png", "gh4.png", "gh5.png"]
SPRITES_PATH = ["Blinky.png", "Inky.png", "Pinky.png", "Clyde.png",
                "Pacman.png", "PacmanDeath.png"]


class UnitAnimation:
    def __init__(self, file_name, size, label):
        self.frame_size = size
        self.current_frame = 0
        self.label = label
        self.current_direction = Direction.left
        self.sprites = self.unpack_sprites(GameField.SPRITES[file_name])
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.timer.start(70)

    def next_frame(self):
        self.current_frame += 1
        if self.current_frame >= len(self.sprites[self.current_direction]):
            self.current_frame = 0

        self.label.setPixmap(self.get_current_pixmap())

    def get_current_pixmap(self):
        return self.sprites[self.current_direction][self.current_frame]

    def unpack_sprites(self, input_pixmap):
        result = {Direction.right: [], Direction.left: [],
                  Direction.up: [], Direction.down: []}
        keys = [Direction.right,  Direction.left, Direction.up, Direction.down]
        current_key = 0
        frame_count = input_pixmap.width() // (self.frame_size.width() * 4)

        for current_frame in range(frame_count * 4):
            frame = input_pixmap.copy(current_frame * self.frame_size.width(),
                                      0, self.frame_size.width(),
                                      self.frame_size.height())

            result[keys[current_key]].append(frame)
            if (current_frame + 1) % frame_count == 0:
                current_key += 1

        return result


class PacmanDeathAnimation:
    def __init__(self, file_name, size, label):
        self.current_frame = 0
        self.frame_size = size
        self.label = label
        self.sprites = self.unpack_sprites(GameField.SPRITES[file_name])

        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)

    def next_frame(self):
        self.current_frame += 1
        if self.current_frame >= len(self.sprites) - 1:
            self.current_frame = 0
            self.timer.stop()
        else:
            self.label.setPixmap(self.sprites[self.current_frame])
            self.label.update()

    def unpack_sprites(self, filename):
        input_pixmap = QPixmap(filename)
        frame_count = input_pixmap.width() // self.frame_size.width()
        width = self.frame_size.width()
        sprites = []

        for current_frame in range(1, frame_count+1):
            sprites.append(input_pixmap.copy(current_frame * width, 0,
                                             width, self.frame_size.height()))

        return sprites


class GameField(QGraphicsView):
    PIXMAPS = {}
    SPRITES = {}

    def __init__(self, parent_window, game):
        super().__init__(parent_window)
        self.item_size = QSize(32, 32)
        self.map = game.game_map
        self.game = game
        self.map_painter = QPainter()
        self.scene = QGraphicsScene()
        GameField.PIXMAPS = self.load_pixmaps()
        GameField.SPRITES = self.load_sprites()

        self.init_default_state()
        self.init_map()
        self.pacman_animation = PacmanGrapghic(self, self.game.pacman,
                                               self.item_size)
        self.ghosts_animation = self.init_ghosts_animation()
        self.show()

    def init_ghosts_animation(self):
        ghosts_animation = []
        ghost_size = QSize(26, 26)
        for ghost in self.game.ghosts:
            ghosts_animation.append(GhostGraphic(self, ghost, ghost_size))
        return ghosts_animation

    def init_default_state(self):
        self.scene.setBackgroundBrush(Qt.black)
        self.scene.setSceneRect(0, 0, 608, 608)
        self.setFixedSize(608, 608)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setScene(self.scene)

    def init_map(self):
        with open('map.txt') as map_file:
            for (i, cells) in enumerate(map_file):
                for (j, cell) in enumerate(cells):
                    if cell in self.PIXMAPS.keys():
                        self.scene.addItem(MapItem(self.PIXMAPS[cell],
                                                   j, i, self.item_size))

    def build_ghost_house(self, x, y):
        for i in range(5):
            current_pixmap = QPixmap("ghostHouse{}.png".format(i + 1))
            self.scene.addItem(MapItem(current_pixmap, x + i, y,
                                       self.item_size))

    def keyPressEvent(self, key_event):
        if key_event.key() in directions:
            self.game.pacman.next_direction = key_event.key()

    def load_pixmaps(self):
        images_folder_path = os.path.join(os.path.curdir, "Images")
        default_pixmaps = self.init_default_pixmaps()
        pixmaps = {}

        i = 0
        for name in MAP_ITEMS_PATHS:
            img_path = os.path.join(images_folder_path, name)
            if os.path.exists(img_path):
                pixmaps[str(i)] = QPixmap(img_path)
            else:
                if name in default_pixmaps.keys():
                    pixmaps[name] = default_pixmaps[name]
                    print("WARNING: image file {0} doesn't exist. This image "
                          "was replaced by default value".format(name))
            i += 1

        return pixmaps

    def load_sprites(self):
        images_folder_path = os.path.join(os.path.curdir, "Images")
        sprites = {}
        for name in SPRITES_PATH:
            img_path = os.path.join(images_folder_path, name)
            if os.path.exists(img_path):
                sprites[name] = QPixmap(img_path)
            else:
                raise FileNotFoundError(name)
        return sprites

    def init_default_pixmaps(self):
        default_pixmaps = {}
        for name, color in [("food.png", Qt.white), ("wall.png", Qt.darkBlue),
                            ("empty.png", Qt.black)]:
            default_pixmaps[name] = QPixmap(32, 32)
            default_pixmaps[name].fill(color)

        return default_pixmaps

    def show_game_over_dialog(self):
        dialog = GameOverDialog(1, self)
        result = dialog.exec_()

        if dialog.textValue() != "":
            self.game.update_records(dialog.textValue(),
                                     self.game.pacman.scores)

        if result == QDialog.Accepted:
            QCoreApplication.instance().quit()
        else:
            self.game.restart()
            self.scene.clear()
            self.init_map()
            self.update()
        print(dialog.textValue())


class PacmanGrapghic(QLabel):
    def __init__(self, game_field, pacman, size):
        super().__init__(game_field)
        self.animation = UnitAnimation(pacman.name + '.png', size, self)
        self.death_animation = PacmanDeathAnimation("PacmanDeath.png",
                                                    self.animation.frame_size,
                                                    self)
        self.motion_timer = QTimer()
        self.pacman = pacman

        self.init_start_state()
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(game_field.item_size)

    def init_start_state(self):
        self.move(self.pacman.x * self.width(), self.pacman.y * self.height())
        self.setPixmap(self.animation.get_current_pixmap())
        self.motion_timer.timeout.connect(self.move_unit)
        self.motion_timer.start(170)

    def move_unit(self):
        if not self.animation.timer.isActive():
            if not self.death_animation.timer.isActive():
                self.clear()
                self.pacman.init_start_state()
                self.animation.timer.start(70)
        else:
            if self.pacman.is_dead:
                game_field = self.parent()
                ghosts = game_field.game.ghosts
                for ghost in ghosts:
                    ghost.init_start_state()

                self.animation.timer.stop()
                self.death_animation.timer.start(70)
                self.clear()

                if self.pacman.lifes < 0:
                    game_field.show_game_over_dialog()

            else:
                self.pacman.move()
                x_pos = self.pacman.x * self.width()
                y_pos = self.pacman.y * self.height()
                pacman_direction = self.pacman.current_direction
                self.animation.current_direction = pacman_direction
                self.move(x_pos, y_pos)

                scene = self.parentWidget().scene
                food = scene.itemAt(x_pos, y_pos, QTransform())
                if food is not None:
                    scene.removeItem(food)


class GhostGraphic(QLabel):
    def __init__(self, game_field, ghost, size):
        super().__init__(game_field)
        self.animation = UnitAnimation(ghost.name + '.png', size, self)
        self.motion_timer = QTimer()
        self.ghost = ghost
        self.init_start_state()
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(game_field.item_size)

    def init_start_state(self):
        self.move(self.ghost.x * self.width(), self.ghost.y * self.height())
        self.setPixmap(self.animation.get_current_pixmap())
        self.motion_timer.timeout.connect(self.move_ghost)
        self.motion_timer.start(170) #170

    def move_ghost(self):
        self.ghost.move()
        x_pos = self.ghost.x * self.width()
        y_pos = self.ghost.y * self.height()

        self.animation.current_direction = self.ghost.direction
        self.move(x_pos, y_pos)


class MapItem(QGraphicsItem):
    def __init__(self, pixmap, x, y, size):
        super().__init__()
        self.pixmap = pixmap
        self.size = size
        self.x = x * self.size.width()
        self.y = y * self.size.height()

    def boundingRect(self):
        return QRectF(self.x, self.y, self.size.width(), self.size.height())

    def paint(self, painter, style, widget=None):
        painter.drawPixmap(self.x, self.y, self.size.width(),
                           self.size.height(), self.pixmap)


class GameOverDialog(QInputDialog):
    def __init__(self, scores, parent=None):
        super().__init__(parent)
        self.widget = QWidget()
        self.setLabelText("Enter your name, high scorer!")
        self.setOkButtonText("Exit")
        self.setCancelButtonText("Try again")
        self.setWindowModality(2)
        self.setModal(True)
        self.show()


