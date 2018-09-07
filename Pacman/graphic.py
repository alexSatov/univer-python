from PyQt5.QtGui import QPixmap, QPainter, QTransform
from PyQt5.QtCore import QTimer, Qt, QRectF, QSize, QCoreApplication
from PyQt5.QtWidgets import (QGraphicsScene, QGraphicsItem, QGraphicsView,
                             QLabel, QDialog, QWidget, QInputDialog)
from music import Music
from logic import Direction, directions, GameMapItem


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

        for current_frame in range(1, frame_count + 1):
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
        self.weapon_animation = WeaponGraphic(self, self.game.pacman.weapon,
                                              self.item_size)
        self.pacman_animation = PacmanGraphic(self, self.game.pacman,
                                              self.item_size)
        self.blinky_animation = GhostGraphic(self, game.blinky, QSize(26, 26))
        self.pinky_animation = GhostGraphic(self, game.pinky, QSize(26, 26))
        self.inky_animation = GhostGraphic(self, game.inky, QSize(26, 26))
        self.clyde_animation = GhostGraphic(self, game.clyde, QSize(26, 26))

        self.check_states_timer = QTimer()
        self.check_states_timer.timeout.connect(self.check_states)
        self.check_states_timer.start(10)

    def check_states(self):
        self.game.blinky.check_self_death()
        self.game.blinky.check_pacman_death()
        self.game.pinky.check_self_death()
        self.game.pinky.check_pacman_death()
        self.game.inky.check_self_death()
        self.game.inky.check_pacman_death()
        self.game.clyde.check_self_death()
        self.game.clyde.check_pacman_death()

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

    def mousePressEvent(self, QMouseEvent):
        x, y = QMouseEvent.x()//32, QMouseEvent.y()//32
        if self.game.map[y][x] is not GameMapItem.wall:
            self.game.pacman.x, self.game.pacman.y = x, y
            self.game.pacman.is_teleported = True

    def keyPressEvent(self, key_event):
        if key_event.key() in directions:
            self.game.pacman.next_direction = key_event.key()
        if key_event.key() == 69:
            self.add_wall()
        if key_event.key() == 70:
            self.game.pacman.weapon.attack()

    def add_wall(self):
        if self.game.pacman.scores >= 200:
            pacman_direction = self.game.pacman.current_direction
            wall_x = self.game.pacman.x - directions[pacman_direction].x
            wall_y = self.game.pacman.y - directions[pacman_direction].y
            if not self.game.is_ghost(wall_x, wall_y)\
                    and wall_x != 0 and wall_x != 18\
                    and (wall_x, wall_y) not in [(7, 7), (8, 7), (9, 7),
                                                 (10, 7), (11, 7)]:
                wall_pixmap = QPixmap('wall.png')
                self.game.map[wall_y][wall_x] = GameMapItem.wall
                self.scene.addItem(MapItem(wall_pixmap, wall_x, wall_y,
                                           self.item_size))
                self.game.pacman.scores -= 200

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

    def init_ghosts(self):
        self.game.blinky.init_start_state()
        self.game.pinky.init_start_state()
        self.game.inky.init_start_state()
        self.game.clyde.init_start_state()


class GameOverDialog(QInputDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setLabelText("Enter your name, high scorer!")
        self.setOkButtonText("Exit")
        self.setCancelButtonText("Try again")
        self.setWindowModality(2)
        self.setModal(True)
        self.show()


class WeaponGraphic(QLabel):
    def __init__(self, game_field, weapon, size):
        super().__init__(game_field)
        self.animation = UnitAnimation(weapon.name + '.png', size, self)
        self.death_animation = DeathAnimation(weapon.name + 'Death.png',
                                              self.animation.frame_size,
                                              self)
        self.motion_timer = QTimer()
        self.weapon = weapon

        self.init_start_state()
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(game_field.item_size)

    def init_start_state(self):
        self.move(self.weapon.x * self.width(), self.weapon.y * self.height())
        self.setPixmap(self.animation.get_current_pixmap())
        self.motion_timer.timeout.connect(self.move_unit)
        self.motion_timer.start(85)

    def move_unit(self):
        if not self.animation.timer.isActive():
            if not self.death_animation.timer.isActive():
                self.clear()
                self.weapon.init_start_state()
                self.move(self.weapon.x * self.width(),
                          self.weapon.y * self.height())
                self.animation.timer.start(70)
        else:
            if self.weapon.is_dead:
                self.animation.timer.stop()
                self.death_animation.timer.start(70)
                self.clear()
            else:
                self.do_movement()

    def do_movement(self):
        self.weapon.move()
        x_pos = self.weapon.x * self.width()
        y_pos = self.weapon.y * self.height()
        self.animation.current_direction = self.weapon.direction
        self.move(x_pos, y_pos)


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
        Music.start()
        self.motion_timer.timeout.connect(self.move_unit)
        self.motion_timer.start(170)

    def move_unit(self):
        game_field = self.parent()
        if not self.animation.timer.isActive():
            if not self.death_animation.timer.isActive():
                self.clear()
                self.pacman.init_start_state()
                self.do_movement()
                self.animation.timer.start(70)
        else:
            if self.pacman.is_dead:
                game_field.init_ghosts()
                Music.death()
                self.animation.timer.stop()
                self.death_animation.timer.start(70)
                self.clear()
                if self.pacman.lifes < 0:
                    game_field.show_game_over_dialog()
            else:
                self.check_compliting_level(game_field)
                self.pacman.move()
                self.do_movement()

    def do_movement(self):
        x_pos = self.pacman.x * self.width()
        y_pos = self.pacman.y * self.height()
        pacman_direction = self.pacman.current_direction
        self.animation.current_direction = pacman_direction
        self.move(x_pos, y_pos)
        scene = self.parentWidget().scene
        food = scene.itemAt(x_pos, y_pos, QTransform())
        if food is not None and self.pacman.x not in [0, 18]:
            scene.removeItem(food)
            if self.pacman.eaten_food % 2 == 1:
                Music.waka()

    def check_compliting_level(self, game_field):
        if self.pacman.game.is_level_complete:
            game_field.game.level += 1
            game_field.game.restart()
            game_field.scene.clear()
            game_field.init_map()
            game_field.scene.update()


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
        self.motion_timer.start(210)

    def move_ghost(self):
        if self.ghost.is_dead:
            self.ghost.pacman.scores += 100
            self.ghost.init_start_state()
        else:
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
