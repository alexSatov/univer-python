import sys
import math
from enum import IntEnum
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])
Way = namedtuple('Way', ['dir', 'dist'])
Record = namedtuple('Record', ['name', 'score'])


class Direction(IntEnum):
    left = 65
    right = 68
    up = 87
    down = 83


class GameMapItem(IntEnum):
    empty = 2
    food = 0
    wall = 1

directions = {Direction.left: Point(-1, 0),
              Direction.right: Point(1, 0),
              Direction.down: Point(0, 1),
              Direction.up: Point(0, -1)}


class Game:
    def __init__(self):
        self.map = []
        self.is_level_complete = False
        self.level = 1
        self.init_map()
        self.pacman = Pacman(self)
        self.pacman.weapon = FireBall(self)
        self.blinky = Blinky(self.pacman)
        self.pinky = Pinky(self.pacman)
        self.inky = Inky(self.pacman, self.blinky)
        self.clyde = Clyde(self.pacman)

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, level):
        if level > 3:
            self._level = 1
        else:
            self._level = level

    def init_map(self):
        try:
            with open('level{}.txt'.format(self.level)) as file:
                i = 0
                for cells in file:
                    self.map.append([])
                    for cell in cells:
                        if cell == '1':
                            self.map[i].append(GameMapItem.wall)
                        if cell == '0':
                            self.map[i].append(GameMapItem.food)
                        if cell == '2':
                            self.map[i].append(GameMapItem.empty)
                    i += 1
        except FileNotFoundError:
            print('Missing level file')
            sys.exit()

    def new_game(self, level=1):
        self.pacman.set_default_params()
        self.level = level
        self.restart()

    def restart(self):
        self.map = []
        self.init_map()
        self.blinky.init_start_state()
        self.pinky.init_start_state()
        self.inky.init_start_state()
        self.clyde.init_start_state()
        self.pacman.init_start_state()
        self.is_level_complete = False

    def is_ghost(self, x, y):
        return self.blinky.x == x and self.blinky.y == y or \
               self.pinky.x == x and self.pinky.y == y or \
               self.inky.x == x and self.inky.y == y or \
               self.clyde.x == x and self.clyde.y == y

    def update_records(self, name, scores):
        records = self.get_records_list()
        try:
            with open('records.txt', "w+", encoding='utf-8') as records_file:
                records.append(Record(name, scores))
                records = list(set(records))
                records.sort(key=lambda rec: rec.score, reverse=True)
                for player_name, player_scores in records:
                    record = "{0} {1}\n".format(player_name, player_scores)
                    records_file.write(record)
        except FileNotFoundError:
            print('Missing records file')
            sys.exit()

    def cheat(self, cheat_command):
        if cheat_command == 'god':
            self.pacman.lifes = 9999
        if cheat_command == 'level2':
            self.new_game(2)
        if cheat_command == 'level3':
            self.new_game(3)

    @staticmethod
    def get_records_list():
        records = []
        try:
            with open('records.txt', encoding='utf-8') as records_file:
                for record in records_file:
                    if len(record) > 2:
                        score = int(record.split(' ')[1])
                        name = record.split(' ')[0]
                        records.append(Record(name, score))
        except FileNotFoundError:
            print('Missing records file')
            sys.exit()
        return records


class FireBall:
    def __init__(self, game):
        self.game = game
        self.name = 'FireBall'
        self.x = -1
        self.y = -1
        self.is_active = False
        self.is_dead = False
        self.direction = self.game.pacman.current_direction

    def init_start_state(self):
        self.x = -1
        self.y = -1
        self.is_dead = False
        self.is_active = False

    def attack(self):
        pacman_direction = self.game.pacman.current_direction
        x = self.game.pacman.x + directions[pacman_direction].x
        y = self.game.pacman.y + directions[pacman_direction].y
        if x == 19:
            x -= 1
        if not self.is_active and self.game.map[y][x] is not GameMapItem.wall:
            self.is_active = True
            self.direction = pacman_direction
            self.x = x
            self.y = y

    def move(self):
        if self.is_active:
            if self.is_clear_way():
                self.x += directions[self.direction].x
                self.y += directions[self.direction].y
            else:
                self.is_dead = True

    def is_clear_way(self):
        next_x = self.x + directions[self.direction].x
        next_y = self.y + directions[self.direction].y
        if next_x == 18 or next_x == 0:
            return False
        try:
            return self.game.map[next_y][next_x] is not GameMapItem.wall
        except IndexError:
            return False


class Pacman:
    def __init__(self, game):
        self.scores = 0
        self.game = game
        self.lifes = 2
        self.eaten_food = 0
        self.x = 9
        self.y = 13
        self.is_dead = False
        self.is_teleported = False
        self.current_direction = Direction.left
        self.next_direction = Direction.left
        self.weapon = None
        self.game.map[self.y][self.x] = self

    def move(self):
        if not self.is_teleported:
            self.check_food()
            self.game.map[self.y][self.x] = GameMapItem.empty
            if self.is_clear_way(self.next_direction):
                self.current_direction = self.next_direction
                self.x += directions[self.current_direction].x
                self.y += directions[self.current_direction].y
            elif self.is_clear_way(self.current_direction):
                self.x += directions[self.current_direction].x
                self.y += directions[self.current_direction].y
            self.check_portal()
            self.check_food()
            self.game.map[self.y][self.x] = self
        else:
            self.is_teleported = False

    def is_clear_way(self, direction):
        next_x = self.x + directions[direction].x
        next_y = self.y + directions[direction].y
        if next_x == 19 or next_x == -1:
            return True
        return self.game.map[next_y][next_x] is not GameMapItem.wall

    def check_food(self):
        if self.game.map[self.y][self.x] is GameMapItem.food:
            self.scores += 10
            self.eaten_food += 1
            food_count = 0
            for cells in self.game.map:
                for cell in cells:
                    if cell is GameMapItem.food:
                        food_count += 1
            if food_count == 1:
                self.game.is_level_complete = True
                self.eaten_food = 0

    def check_portal(self):
        is_right_portal = self.x == 19 and self.y == 8 and \
            self.current_direction == Direction.right
        is_left_portal = self.x == -1 and self.y == 8 and \
            self.current_direction == Direction.left
        if is_right_portal:
            self.x = 0
            self.y = 8
        if is_left_portal:
            self.x = 18
            self.y = 8

    def init_start_state(self):
        self.x = 9
        self.y = 13
        self.is_dead = False
        self.current_direction = Direction.left
        self.next_direction = Direction.left

    def set_default_params(self):
        self.eaten_food = 0
        self.scores = 0
        self.lifes = 2
        self.init_start_state()


def distance_between_positions(position1, position2):
    x = position2.x - position1.x
    y = position2.y - position1.y
    return math.sqrt(math.pow(x, 2) + math.pow(y, 2))


class Ghost:
    def __init__(self, pacman, name, x, y):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.in_house = True
        self.is_dead = False
        self.name = name
        self.pacman = pacman
        self.target = Point(pacman.x, pacman.y)
        self.direction = Direction.left
        self.steps = 0

    def init_start_state(self):
        self.x = self.start_x
        self.y = self.start_y
        self.direction = Direction.left
        self.in_house = True
        self.is_dead = False
        self.steps = 0

    def move(self):
        self.check_pacman_death()
        self.choose_way()
        self.x += directions[self.direction].x
        self.y += directions[self.direction].y
        self.check_pacman_death()
        self.steps += 1

    def check_self_death(self):
        if (self.x, self.y) == (self.pacman.weapon.x, self.pacman.weapon.y):
            self.is_dead = True
            self.pacman.weapon.is_dead = True

    def check_pacman_death(self):
        if self.x == self.pacman.x and self.y == self.pacman.y:
            if not self.pacman.is_dead:
                self.pacman.lifes -= 1
            self.pacman.is_dead = True

    def get_wall_count(self):
        positions = [(self.y, self.x - 1), (self.y, self.x + 1),
                     (self.y + 1, self.x), (self.y - 1, self.x)]
        wall_count = 0
        for y, x in positions:
            if self.pacman.game.map[y][x] == GameMapItem.wall or \
                                    y == 8 and (x == 0 or x == 18):
                wall_count += 1
        return wall_count

    def get_previous_direction(self):
        prev_direction = None
        if self.direction is Direction.up:
            prev_direction = Direction.down
        if self.direction is Direction.down:
            prev_direction = Direction.up
        if self.direction is Direction.left:
            prev_direction = Direction.right
        if self.direction is Direction.right:
            prev_direction = Direction.left
        return prev_direction

    def choose_way(self):
        wall_count = self.get_wall_count()
        prev_direction = self.get_previous_direction()
        possible_ways = self.get_possible_ways()
        if wall_count < 2:
            correct_ways = []
            for direction in possible_ways:
                if possible_ways[direction] is not None:
                    way = Way(direction, distance_between_positions(
                        possible_ways[direction], self.target))
                    correct_ways.append(way)
            correct_ways.sort(key=lambda item: item.dist)
            self.direction = correct_ways[0].dir
        elif wall_count == 3:
            self.direction = prev_direction
        else:
            if not self.is_clear_way():
                for direction in possible_ways:
                    if possible_ways[direction] is not None:
                        self.direction = direction

    def get_possible_ways(self):
        prev_way = Point(self.x - directions[self.direction].x,
                         self.y - directions[self.direction].y)
        possible_ways = {}
        for direction in directions:
            possible_ways[direction] = Point(self.x + directions[direction].x,
                                             self.y + directions[direction].y)
        for direction in possible_ways:
            cell = possible_ways[direction]
            if self.pacman.game.map[cell.y][cell.x] is GameMapItem.wall \
                    or cell == prev_way:
                possible_ways[direction] = None
        return possible_ways

    def is_clear_way(self):
        next_x = self.x + directions[self.direction].x
        next_y = self.y + directions[self.direction].y
        if next_x == 18 or next_x == 0:
            return False
        return self.pacman.game.map[next_y][next_x] is not GameMapItem.wall


class Blinky(Ghost):
    def __init__(self, pacman):
        super().__init__(pacman, 'Blinky', 9, 7)
        self.escape_target = Point(17, -2)

    def update_target(self):
        if self.steps < 15:
            self.target = Point(self.pacman.x, self.pacman.y)
        else:
            self.target = self.escape_target
            if self.steps == 18:
                self.steps = 0

    def move(self):
        if not self.pacman.is_dead:
            self.update_target()
            Ghost.move(self)


class Pinky(Ghost):
    def __init__(self, pacman):
        super().__init__(pacman, 'Pinky', 9, 8)
        self.escape_target = Point(1, -2)

    def update_target(self):
        if self.steps < 15:
            dx = directions[self.pacman.current_direction].x * 4
            dy = directions[self.pacman.current_direction].y * 4
            self.target = Point(self.pacman.x + dx, self.pacman.y + dy)
        else:
            self.target = self.escape_target
            if self.steps == 18:
                self.steps = 0

    def move(self):
        if not self.pacman.is_dead:
            if self.in_house:
                self.start_move()
            else:
                self.update_target()
                Ghost.move(self)

    def start_move(self):
        self.direction = Direction.up
        self.y -= 1
        self.in_house = False


class Inky(Ghost):
    def __init__(self, pacman, blinky):
        super().__init__(pacman, 'Inky', 7, 8)
        self.blinky = blinky
        self.escape_target = Point(17, 20)
        self.start_step = 0

    def update_target(self):
        if self.steps < 15:
            dx = directions[self.pacman.current_direction].x * 2
            dy = directions[self.pacman.current_direction].y * 2
            vector_start = Point(self.blinky.x, self.blinky.y)
            vector_end = Point(self.pacman.x + dx, self.pacman.y + dy)
            vector = Point(vector_end.x - vector_start.x,
                           vector_end.y - vector_start.y)
            self.target = Point(vector_end.x + vector.x,
                                vector_end.y + vector.y)
        else:
            self.target = self.escape_target
            if self.steps == 18:
                self.steps = 0

    def move(self):
        if not self.pacman.is_dead:
            if self.in_house:
                if self.pacman.eaten_food >= 30:
                    self.start_move()
            else:
                self.update_target()
                Ghost.move(self)

    def start_move(self):
        if self.start_step == 0 or self.start_step == 1:
            self.direction = Direction.right
            self.x += 1
            self.start_step += 1
        elif self.start_step == 2:
            self.direction = Direction.left
            self.y -= 1
            self.in_house = False
            self.start_step = 0


class Clyde(Ghost):
    def __init__(self, pacman):
        super().__init__(pacman, 'Clyde', 11, 8)
        self.escape_target = Point(1, 20)
        self.start_step = 0

    def update_target(self):
        if self.steps < 15:
            distance_to_pacman = distance_between_positions(
                Point(self.x, self.y),
                Point(self.pacman.x, self.pacman.y))
            if distance_to_pacman <= 8:
                self.target = Point(self.pacman.x, self.pacman.y)
            else:
                self.target = self.escape_target
        else:
            self.target = self.escape_target
            if self.steps == 18:
                self.steps = 0

    def move(self):
        if not self.pacman.is_dead:
            if self.in_house:
                if self.pacman.eaten_food >= 72:
                    self.start_move()
            else:
                self.update_target()
                Ghost.move(self)

    def start_move(self):
        if self.start_step == 0 or self.start_step == 1:
            self.direction = Direction.left
            self.x -= 1
            self.start_step += 1
        elif self.start_step == 2:
            self.direction = Direction.right
            self.y -= 1
            self.in_house = False
            self.start_step = 0
