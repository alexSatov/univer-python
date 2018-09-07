import random


class GameField:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = self.init_empty_field()
        # for undo:
        self.last_added = []

    def init_empty_field(self):
        empty_field = []
        for x in range(self.width):
            empty_field.append([])
            for y in range(self.height):
                empty_field[x].append(0)
        return empty_field

    def get_coord_of_same_balls(self, x, y, dx, dy, ball_color):
        suitable_balls = []
        while self._get_color_of_ball(x + dx, y + dy) == ball_color:
            x += dx
            y += dy
            suitable_balls.append((x, y))
        return suitable_balls

    def set_in_random_empty_cell(self, value):
        while True:
            rand_x = random.randint(0, self.width - 1)
            rand_y = random.randint(0, self.height - 1)
            if self.is_empty_cell(rand_x, rand_y):
                self.cells[rand_x][rand_y] = value
                self.last_added.append((rand_x, rand_y))
                break

    def _get_color_of_ball(self, x, y):
        return -1 if self.is_out_of_borders(x, y) else self.cells[x][y]

    def is_empty_cell(self, x, y):
        return self.cells[x][y] == 0

    def is_exists_empty_cells(self):
        for row in self.cells:
            if 0 in row: return True

        return False

    def is_out_of_borders(self, x, y):
        return not (0 <= x < self.width and 0 <= y < self.height)
