from random import randint
import queue
from collections import namedtuple

GameSettings = namedtuple("GameSettings", ["colors_count",
                                           "next_balls_lim",
                                           "line_length"])
OFFSETS = [(1, 0), (0, 1), (1, 1), (-1, 1)]


class Game:
    def __init__(self, game_field, game_settings=GameSettings(7, 3, 5)):
        self.field = game_field
        self.next_balls_color = []
        self.user_scores = 0
        self.ball_count = 0
        self.game_settings = game_settings
        self.init_start_state()
        self.selected_location = None
        #_________ for undo:
        self.previous_location = None


    def init_start_state(self):
        self.field.cells = self.field.init_empty_field()
        self.ball_count = 0
        self.user_scores = 0
        self.init_next_balls_color()
        self.set_next_balls_on_field()
        self.init_next_balls_color()

    def move_ball(self, target_x, target_y):
        x, y = self.selected_location
        self.previous_location = self.selected_location
        self.field.cells[target_x][target_y] = self.field.cells[x][y]
        self.field.cells[x][y] = 0
        self.selected_location = target_x, target_y

    def next_step(self):
        balls_seq = self.get_longest_seq_of_same_balls(*self.selected_location)
        if len(balls_seq) >= self.game_settings.line_length:
            self.remove_line(balls_seq)
            self.add_scores(len(balls_seq))
        else:
            self.set_next_balls_on_field()
            self.init_next_balls_color()

    def add_scores(self, removed_balls_count):
        line_lim = self.game_settings.line_length
        self.user_scores += (removed_balls_count + 1 - line_lim) * removed_balls_count

    def get_longest_seq_of_same_balls(self, x, y):
        start_ball_color = self.field.cells[x][y]
        get_same_balls = self.field.get_coord_of_same_balls
        balls_seq = []

        for dx, dy in OFFSETS:
            current_balls = get_same_balls(x, y, dx, dy, start_ball_color)
            current_balls.append((x, y))
            balls_in_opposite_direction = get_same_balls(x, y, -dx, -dy,
                                                         start_ball_color)
            current_balls.extend(balls_in_opposite_direction)
            if len(current_balls) > len(balls_seq):
                balls_seq = current_balls
        return balls_seq

    def remove_line(self, balls_coord):
        self.selected_location = None
        for x, y in balls_coord:
            self.field.cells[x][y] = 0
        self.ball_count -= len(balls_coord)

    def set_next_balls_on_field(self):
        self.field.last_added = []
        self.ball_count += len(self.next_balls_color)
        for ball in self.next_balls_color:
            self.field.set_in_random_empty_cell(ball)

    def init_next_balls_color(self):
        max_val = self.game_settings.colors_count
        balls_lim = self.game_settings.next_balls_lim
        self.next_balls_color = [randint(1, max_val) for i in range(balls_lim)]

    def is_game_over(self,):
        max_balls_count = self.field.width * self.field.height
        return self.ball_count + len(self.next_balls_color) >= max_balls_count

    def is_possible_to_move_ball(self, target_x, target_y):
        used_vertices = []
        opened_vertices = queue.Queue()
        opened_vertices.put(self.selected_location)
        used_vertices.append(self.selected_location)

        while not opened_vertices.empty():
            current_coord = opened_vertices.get()

            if current_coord == (target_x, target_y):
                return True

            if self.field.is_out_of_borders(*current_coord) or not self.field.is_empty_cell(*current_coord) and current_coord != self.selected_location:
                continue

            x, y = current_coord
            for dx, dy in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                next_coord = (x + dx, y + dy)
                if next_coord not in used_vertices:
                    opened_vertices.put(next_coord)
                    used_vertices.append(next_coord)

        return False

    def undo_action(self):
        self.move_ball(*self.previous_location)
        self.remove_line(self.field.last_added)
        print("undo")
