import math
import io
from enum import IntEnum


class Direction(IntEnum):
    left = 16777234
    right = 16777236
    up = 16777235
    down = 16777237


directions = {Direction.left: (-1, 0),
              Direction.right: (1, 0),
              Direction.down: (0, 1),
              Direction.up: (0, -1)}


class MapItem(IntEnum):
    empty = 2
    food = 0
    wall = 1


class Game:
    def __init__(self):
        self.game_map = []
        self.pacman = Pacman(self.game_map)
        blinky = Blinky(self.pacman)
        self.ghosts = [Inky(self.pacman, blinky), Pinky(self.pacman), blinky,
                       Clyde(self.pacman)]

        self.init_map()
        for ghost in self.ghosts:
            ghost.init_start_state()

    def init_game(self):
        self.game_map[9][13] = self.pacman

    def init_map(self):
        map_items = {'1': MapItem.wall, '0': MapItem.food, '2': MapItem.empty}
        for code in range(3, 8):
            map_items[str(code)] = MapItem.wall

        with open('map.txt') as map_file:
            for (i, cells) in enumerate(map_file):
                self.game_map.append([])
                for cell in cells.strip():
                    if cell in map_items.keys():
                        self.game_map[i].append(map_items[cell])
                        pos_code = int(cell)
                        if 3 <= pos_code <= 6:
                            x = len(self.game_map[i])
                            self.ghosts[pos_code-3].set_start_pos(x, i)

    def restart(self):
        self.game_map = []
        self.init_map()
        for ghost in self.ghosts:
            ghost.init_start_state()
        self.pacman.set_default_params(self.game_map)

    def update_records(self, name, scores):
        records = self.get_records_list()

        with open('records.txt', "a+") as records_file:
            new_record = "{0} {1}\n".format(name, scores)
            if len(records) == 0 or records[0][1] < scores:
                records_file.seek(0)
                records_file.write(new_record)
            elif records[len(records) - 1][1] > scores:
                records_file.seek(io.SEEK_END)
                records_file.write(new_record)
                return

        with open('records.txt', "w+") as records_file:
            records.append((name, scores))
            records.sort(key=lambda rec: rec[1], reverse=True)
            for player_name, player_scores in records:
                record = "{0} {1}\n".format(player_name, player_scores)
                records_file.write(record)

    def get_records_list(self):
        records = []
        with open('records.txt', 'a+') as records_file:
            for record in records_file:
                score = int(record.split(' ')[1])
                name = record.split(' ')[0]
                records.append((name, score))
        return records


class Pacman:
    def __init__(self, game_map):
        self.scores = 0
        self.lifes = 2
        self.x = 9
        self.y = 13
        self.game_map = game_map
        self.is_dead = False
        self.name = 'Pacman'
        self.current_direction = Direction.left
        self.next_direction = Direction.left

    def move(self):
        self.game_map[self.y][self.x] = MapItem.empty
        if self.is_clear_way(self.next_direction):
            self.current_direction = self.next_direction
            self.x += directions[self.current_direction][0]
            self.y += directions[self.current_direction][1]
        elif self.is_clear_way(self.current_direction):
            self.x += directions[self.current_direction][0]
            self.y += directions[self.current_direction][1]

        self.check_portal()
        self.check_food()
        self.game_map[self.y][self.x] = self

    def is_clear_way(self, direction):
        next_x = self.x + directions[direction][0]
        next_y = self.y + directions[direction][1]

        if next_x == 19 or next_x == -1:
            return True

        return self.game_map[next_y][next_x] is not MapItem.wall

    def check_food(self):
        if self.game_map[self.y][self.x] is MapItem.food:
            self.scores += 10

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

    def set_default_params(self, map):
        self.game_map = map
        self.scores = 0
        self.lifes = 2
        self.init_start_state()


def distance_between_positions(position1, position2):
    x = position2[0] - position1[0]
    y = position2[1] - position1[1]
    return math.sqrt(math.pow(x, 2) + math.pow(y, 2))


class Ghost:
    def __init__(self, pacman, name):
        self.in_house = True
        self.is_dead = False
        self.name = name
        self.x = 0
        self.y = 0
        self.start_x = 0
        self.start_y = 0

        self.pacman = pacman
        self.game_map = pacman.game_map
        self.target = (pacman.x, pacman.y)
        self.direction = Direction.left
        self.current_direction = Direction.left

    def set_start_pos(self, x, y):
        self.start_x = x
        self.start_y = y

    def init_start_state(self):
        self.x = self.start_x
        self.y = self.start_y
        self.direction = Direction.left
        self.current_direction = Direction.left
        self.in_house = True

    def move(self):
        self.check_pacman_death()
        if not self.is_crossway() and not self.is_clear_way():
            self.turn()
        else:
            self.choose_direction()

        self.x += directions[self.direction][0]
        self.y += directions[self.direction][1]
        self.check_pacman_death()

    def check_pacman_death(self):
        if self.x == self.pacman.x and self.y == self.pacman.y:
            if not self.pacman.is_dead:
                self.pacman.lifes -= 1
            self.pacman.is_dead = True

    def turn(self):
        if self.direction == Direction.up or self.direction == Direction.down:
            left_turn = (self.x + directions[Direction.left][0],
                         self.y + directions[Direction.left][1])
            if self.game_map[left_turn[1]][left_turn[0]] is MapItem.wall:
                self.direction = Direction.right
            else:
                self.direction = Direction.left
        else:
            if self.portal_ahead():
                if self.direction == Direction.left:
                    self.direction = Direction.right
                else:
                    self.direction = Direction.left
            else:
                up_turn = (self.x + directions[Direction.up][0],
                           self.y + directions[Direction.up][1])
                if self.game_map[up_turn[1]][up_turn[0]] is MapItem.wall:
                    self.direction = Direction.down
                else:
                    self.direction = Direction.up

    def portal_ahead(self):
        next_x = self.x + directions[self.direction][0]
        return (next_x == 19 or next_x == 0) and self.y == 8

    def is_crossway(self):
        positions = [(self.y, self.x - 1), (self.y, self.x + 1),
                     (self.y + 1, self.x), (self.y - 1, self.x)]
        wall_counter = 0
        for y, x in positions:
            if not self.is_out_of_borders(x, y) and self.game_map[y][x] == MapItem.wall:
                wall_counter += 1
            if wall_counter == 2:
                return False
        return True

    def choose_direction(self):
        prev_pos = (self.x - directions[self.direction][0],
                    self.y - directions[self.direction][1])
        possible_ways = {}
        for direction in directions:
            possible_ways[direction] = (self.x + directions[direction][0],
                                        self.y + directions[direction][1])
        for direction in possible_ways:
            way = possible_ways[direction]
            if self.game_map[way[1]][way[0]] is MapItem.wall or way == prev_pos:
                possible_ways[direction] = None

        correct_ways = []
        for direction in possible_ways:
            if possible_ways[direction] is not None:
                correct_ways.append((direction,
                                     distance_between_positions(
                                         possible_ways[direction],
                                         self.target)))

        correct_ways.sort(key=lambda item: item[1])
        self.direction = correct_ways[0][0]

    def is_clear_way(self):
        next_x = self.x + directions[self.direction][0]
        next_y = self.y + directions[self.direction][1]
        if next_x == 19 or next_x == 0:
            return False

        return self.game_map[next_y][next_x] is not MapItem.wall

    def is_out_of_borders(self, x, y):
        return x == -1 or x == 19 or y == -1 or y == 19


class Blinky(Ghost):
    def __init__(self, pacman):
        super().__init__(pacman, 'Blinky')
        self.escape_target = (17, -2)
        self.in_house = False
        self.start_y -= 1

    def update_target(self):
        self.target = (self.pacman.x, self.pacman.y)

    def move(self):
        self.update_target()
        Ghost.move(self)


class Pinky(Ghost):
    def __init__(self, pacman):
        super().__init__(pacman, 'Pinky')
        self.escape_target = (1, -2)

    def update_target(self):
        dx = directions[self.pacman.current_direction][0] * 4
        dy = directions[self.pacman.current_direction][1] * 4
        self.target = (self.pacman.x + dx, self.pacman.y + dy)

    def move(self):
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
        super().__init__(pacman, 'Inky')
        self.blinky = blinky
        self.escape_target = (17, 20)
        self.start_step = 0

    def update_target(self):
        dx = directions[self.pacman.current_direction][0] * 2
        dy = directions[self.pacman.current_direction][1] * 2
        vector_start = (self.blinky.x, self.blinky.y)
        vector_end = (self.pacman.x + dx, self.pacman.y + dy)
        vector = (vector_end[0] - vector_start[0],
                  vector_end[1] - vector_start[1])
        self.target = (vector_end[0] + vector[0], vector_end[1] + vector[1])

    def move(self):
        if self.in_house:
            if self.pacman.scores % 300 == 0:
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
            self.direction = Direction.up
            self.y -= 1
            self.in_house = False


class Clyde(Ghost):
    def __init__(self, pacman):
        super().__init__(pacman, 'Clyde')
        self.escape_target = (1, 20)
        self.start_step = 0

    def update_target(self):
        distance_to_pacman = distance_between_positions(
            (self.x, self.y),
            (self.pacman.x, self.pacman.y))
        if distance_to_pacman <= 8:
            self.target = (self.pacman.x, self.pacman.y)
        else:
            self.target = self.escape_target

    def move(self):
        if self.in_house:
            if self.pacman.scores % 720 == 0:
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
            self.direction = Direction.up
            self.y -= 1
            self.in_house = False
