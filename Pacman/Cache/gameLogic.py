import math
from enum import IntEnum
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])
Way = namedtuple('Way', ['dir', 'dist'])
Record = namedtuple('Record', ['name', 'score'])


class Direction(IntEnum):
    left = 16777234
    right = 16777236
    up = 16777235
    down = 16777237


class MapItem(IntEnum):
    empty = 2
    food = 0
    wall = 1

directions = {Direction.left: Point(-1, 0),
              Direction.right: Point(1, 0),
              Direction.down: Point(0, 1),
              Direction.up: Point(0, -1)}


class Game:
    map = []
    food_count = 0
    is_level_complete = False

    def __init__(self):
        self.level = 1
        self.init_map()
        self.pacman = Pacman()
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
        with open('level{}.txt'.format(self.level)) as file:
            i = 0
            for cells in file:
                Game.map.append([])
                for cell in cells:
                    if cell == '1':
                        Game.map[i].append(MapItem.wall)
                    if cell == '0':
                        Game.map[i].append(MapItem.food)
                        Game.food_count += 1
                    if cell == '2':
                        Game.map[i].append(MapItem.empty)
                i += 1

    def new_game(self):
        self.restart()
        self.pacman.set_default_params()

    def restart(self):
        Game.map = []
        self.init_map()
        self.blinky.init_start_state()
        self.pinky.init_start_state()
        self.inky.init_start_state()
        self.clyde.init_start_state()
        self.pacman.init_start_state()
        Game.is_level_complete = False

    def update_records(self, name, scores):
        records = self.get_records_list()

        with open('records.txt', "w+", encoding='utf-8') as records_file:
            records.append(Record(name, scores))
            records = list(set(records))
            records.sort(key=lambda rec: rec.scores, reverse=True)
            for player_name, player_scores in records:
                record = "{0} {1}\n".format(player_name, player_scores)
                records_file.write(record)

    @staticmethod
    def get_records_list():
        records = []
        with open('records.txt', encoding='utf-8') as records_file:
            for record in records_file:
                if len(record) > 2:
                    score = int(record.split(' ')[1])
                    name = record.split(' ')[0]
                    records.append(Record(name, score))
        return records


class FireBall:
    pass


class Pacman:
    def __init__(self):
        self.scores = 0
        self.lifes = 1000
        self.eaten_food = 0
        self.x = 9
        self.y = 13
        self.is_dead = False
        self.current_direction = Direction.left
        self.next_direction = Direction.left

    def move(self):
        Game.map[self.y][self.x] = MapItem.empty
        if self.is_clear_way(self.next_direction):
            self.current_direction = self.next_direction
            self.x += directions[self.current_direction].x
            self.y += directions[self.current_direction].y
        elif self.is_clear_way(self.current_direction):
            self.x += directions[self.current_direction].x
            self.y += directions[self.current_direction].y
        self.check_portal()
        self.check_food()
        Game.map[self.y][self.x] = self

    def is_clear_way(self, direction):
        next_x = self.x + directions[direction].x
        next_y = self.y + directions[direction].y
        if next_x == 19 or next_x == -1:
            return True
        return Game.map[next_y][next_x] is not MapItem.wall

    def check_food(self):
        if Game.map[self.y][self.x] is MapItem.food:
            self.scores += 10
            self.eaten_food += 1
            if self.eaten_food == Game.food_count:
                Game.is_level_complete = True
                Game.food_count = 0
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
        self.lifes = 1000
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
        if not self.is_clear_way():
            self.turn()
        if self.is_crossway():
            self.choose_direction()
        self.x += directions[self.direction].x
        self.y += directions[self.direction].y
        self.check_pacman_death()
        self.steps += 1

    def check_pacman_death(self):
        if self.x == self.pacman.x and self.y == self.pacman.y:
            if not self.pacman.is_dead:
                self.pacman.lifes -= 1
            self.pacman.is_dead = True

    def turn(self):
        possible_ways = self.get_possible_cells()
        possible_ways[self.direction] = None
        prev_direction = None
        if self.direction is Direction.up:
            prev_direction = Direction.down
        if self.direction is Direction.down:
            prev_direction = Direction.up
        if self.direction is Direction.left:
            prev_direction = Direction.right
        if self.direction is Direction.right:
            prev_direction = Direction.left
        turn_direction = None
        possible_ways_count = 0
        for direction in possible_ways:
            if possible_ways[direction] is not None:
                possible_ways_count += 1
                turn_direction = direction
        if possible_ways_count == 0:
            self.direction = prev_direction
        if possible_ways_count == 1:
            self.direction = turn_direction

    def is_crossway(self):
        positions = [(self.y, self.x - 1), (self.y, self.x + 1),
                     (self.y + 1, self.x), (self.y - 1, self.x)]
        wall_counter = 0
        for y, x in positions:
            if Game.map[y][x] == MapItem.wall:
                wall_counter += 1
            if wall_counter == 2:
                return False
        return True

    def get_possible_cells(self):
        prev_cell = Point(self.x - directions[self.direction].x,
                          self.y - directions[self.direction].y)
        possible_cells = {}
        for direction in directions:
            possible_cells[direction] = Point(self.x + directions[direction].x,
                                              self.y + directions[direction].y)
        for direction in possible_cells:
            cell = possible_cells[direction]
            if Game.map[cell.y][cell.x] is MapItem.wall or cell == prev_cell:
                possible_cells[direction] = None
        return possible_cells

    def choose_direction(self):
        possible_cells = self.get_possible_cells()
        correct_cells = []
        for direction in possible_cells:
            if possible_cells[direction] is not None:
                correct_cells.append(Way(direction,
                                     distance_between_positions(
                                         possible_cells[direction],
                                         self.target)))
        correct_cells.sort(key=lambda item: item.dist)
        self.direction = correct_cells[0].dir

    def is_clear_way(self):
        next_x = self.x + directions[self.direction].x
        next_y = self.y + directions[self.direction].y
        if next_x == 18 or next_x == 0:
            return False
        return Game.map[next_y][next_x] is not MapItem.wall


class Blinky(Ghost):
    def __init__(self, pacman):
        super().__init__(pacman, 'Blinky', 9, 7)
        self.escape_target = Point(17, -2)

    def update_target(self):
        if self.steps < 15:
            self.target = Point(self.pacman.x, self.pacman.y)
        elif self.steps == 20:
            self.steps = 0
        else:
            self.target = self.escape_target

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
        elif self.steps == 20:
            self.steps = 0
        else:
            self.target = self.escape_target

    def move(self):
        if not self.pacman.is_dead:
            if self.in_house:
                self.start_move()
            else:
                self.update_target()
                Ghost.move(self)

    def start_move(self):
        self.direction = Direction.right
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
        elif self.steps == 20:
            self.steps = 0
        else:
            self.target = self.escape_target

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
        elif self.steps == 20:
            self.steps = 0
        else:
            self.target = self.escape_target

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
