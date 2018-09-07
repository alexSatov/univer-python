from PyQt5.QtGui import QPixmap, QPainter, QTransform
from PyQt5.QtWidgets import (QGraphicsScene, QGraphicsItem,
                             QGraphicsView, QLabel, QDialog, QWidget,
                             QInputDialog)

from PyQt5.QtCore import QTimer, Qt, QRectF, QSize, QCoreApplication
from logic import Game, Direction, directions


class UnitAnimation:
    def __init__(self, file_name, size, label):
        self.frame_size = size
        self.current_frame = 0
        self.label = label
        self.current_direction = Direction.left
        self.sprites = self.unpack_sprites(QPixmap(file_name))
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
            result[keys[current_key]].append(input_pixmap.copy(
                current_frame * self.frame_size.width(), 0,
                self.frame_size.width(), self.frame_size.height()))
            if (current_frame + 1) % frame_count == 0:
                current_key += 1

        return result


class DeathAnimation:
    def __init__(self, file_name, size, label):
        self.current_frame = 0
        self.frame_size = size
        self.label = label
        self.sprites = self.unpack_sprites(file_name)

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
        sprites = []

        for current_frame in range(1, frame_count+1):
            sprites.append(input_pixmap.copy(
                current_frame * self.frame_size.width(), 0,
                self.frame_size.width(), self.frame_size.height()))
        return sprites


class GameField(QGraphicsView):
    def __init__(self, parent_window, game):
        self.item_size = QSize(32, 32)
        self.map = game.map
        self.game = game
        self.map_painter = QPainter()
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(Qt.black)
        self.scene.setSceneRect(0, 0, 608, 608)
        self.init_map()

        super().__init__(self.scene, parent_window)
        self.setSceneRect(0, 0, 608, 608)
        self.setFixedSize(608, 608)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.show()
        self.pacman_animation = PacmanGraphic(self, self.game.pacman,
                                              self.item_size)
        self.blinky_animation = GhostGraphic(self, game.blinky, QSize(26, 26))
        self.pinky_animation = GhostGraphic(self, game.pinky, QSize(26, 26))
        self.inky_animation = GhostGraphic(self, game.inky, QSize(26, 26))
        self.clyde_animation = GhostGraphic(self, game.clyde, QSize(26, 26))

    def init_map(self):
        wall = QPixmap('wall.png')
        food = QPixmap('food.png')
        empty = QPixmap('empty.png')

        with open('level{}.txt'.format(self.game.level)) as file:
            i = 0
            j = 0
            for cells in file:
                for cell in cells:
                    if cell == '1':
                        self.scene.addItem(MapItem(wall, j, i,
                                                   self.item_size))
                    if cell == '0':
                        self.scene.addItem(MapItem(food, j, i,
                                                   self.item_size))
                    if cell == '2':
                        self.scene.addItem(MapItem(empty, j, i,
                                                   self.item_size))
                    j += 1
                j = 0
                i += 1

                self.build_ghost_house(7, 8)
                self.build_portals()

    def build_ghost_house(self, x, y):
        for i in range(5):
            current_pixmap = QPixmap("ghostHouse{}.png".format(i + 1))
            self.scene.addItem(MapItem(current_pixmap, x + i, y,
                                       self.item_size))

    def build_portals(self):
        blue_portal_pixmap = QPixmap("bluePortal.png")
        orng_portal_pixmap = QPixmap("orangePortal.png")
        self.scene.addItem(MapItem(blue_portal_pixmap, 0, 8, self.item_size))
        self.scene.addItem(MapItem(orng_portal_pixmap, 18, 8, self.item_size))

    def keyPressEvent(self, key_event):
        if key_event.key() in directions:
            self.game.pacman.next_direction = key_event.key()

    def show_game_over_dialog(self):
        dialog = GameOverDialog(self)
        result = dialog.exec_()

        if dialog.textValue() != "":
            self.game.update_records(dialog.textValue(),
                                     self.game.pacman.scores)

        if result == QDialog.Accepted:
            QCoreApplication.instance().quit()
        else:
            self.game.new_game()
            self.scene.clear()
            self.init_map()
            self.update()
        print(dialog.textValue())


class GameOverDialog(QInputDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.widget = QWidget()
        self.setLabelText("Enter your name, high scorer!")
        self.setOkButtonText("Exit")
        self.setCancelButtonText("Try again")
        self.setWindowModality(2)
        self.setModal(True)
        self.show()


class PacmanGraphic(QLabel):
    def __init__(self, game_field, pacman, size):
        super().__init__(game_field)
        self.animation = UnitAnimation('Pacman.png', size, self)
        self.death_animation = DeathAnimation("PacmanDeath",
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
        game_field = self.parent()
        if not self.animation.timer.isActive():
            if not self.death_animation.timer.isActive():
                self.clear()
                self.pacman.init_start_state()
                self.animation.timer.start(70)
        else:
            if self.pacman.is_dead:
                game_field.game.blinky.init_start_state()
                game_field.game.pinky.init_start_state()
                game_field.game.inky.init_start_state()
                game_field.game.clyde.init_start_state()

                self.animation.timer.stop()
                self.death_animation.timer.start(70)
                self.clear()

                if self.pacman.lifes < 0:
                    game_field.show_game_over_dialog()

            else:
                if Game.is_level_complete:
                    if game_field.game.level + 1 > 3:
                        game_field.game.level = 1
                    else:
                        game_field.game.level += 1
                    game_field.game.restart()
                    game_field.scene.clear()
                    game_field.init_map()
                    game_field.scene.update()
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
        self.motion_timer.start(170)

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
