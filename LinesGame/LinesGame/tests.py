import unittest

from gameLogic.game import Game, GameSettings
from gameLogic.gameField import GameField


class GameTests(unittest.TestCase):
    def setUp(self):
        self.gameSettings = GameSettings(7, 3, 5)
        self.gameField = GameField(9, 9)
        self.game = Game(self.gameField, self.gameSettings)
        self.gameField.init_empty_field()

    def test_is_possible_to_move_ball_returnFalse(self):
        balls = [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]
        self.locate_on_playing_field(balls)
        self.game.selected_location = (3, 3)
        result = self.game.is_possible_to_move_ball(0, 0)
        self.assertFalse(result)

    def test_is_possible_to_move_ball_returnTrue(self):
        self.gameField.cells = self.gameField.init_empty_field()
        balls = [(0, 1, 1), (1, 0, 1), (1, 1, 1), (1, 2, 1)]
        self.locate_on_playing_field(balls)
        self.game.selected_location = (2, 0)
        result = self.game.is_possible_to_move_ball(0, 1)
        self.assertTrue(result)

    def locate_on_playing_field(self, balls):
        for x, y, color in balls:
            self.game.field.cells[x][y] = color

    def test_init_next_balls_color(self):
        self.game.init_next_balls_color()
        current_balls_count = len(self.game.next_balls_color)
        expected_count = self.gameSettings.next_balls_lim
        self.assertEqual(expected_count, current_balls_count)

    def test_set_next_balls_on_field(self):
        self.gameField.cells = self.gameField.init_empty_field()
        self.gameField.init_empty_field()
        self.game.init_next_balls_color()
        self.game.set_next_balls_on_field()
        balls = self.get_balls_which_on_field()
        self.assertEqual(self.gameSettings.next_balls_lim, len(balls))

    def get_balls_which_on_field(self):
        balls = []
        for x in range(self.gameField.width):
            for y in range(self.gameField.height):
                ball = self.gameField.cells[x][y]
                if ball != 0:
                    balls.append(ball)
        return balls

    def test_remove_line(self):
        self.gameField.cells = self.gameField.init_empty_field()
        balls = [(0, 1, 1), (0, 0, 2), (1, 0, 3)]
        self.locate_on_playing_field(balls)
        self.expected_result = self.game.ball_count
        self.game.remove_line([(0, 1), (0, 0), (1, 0)])
        balls_on_field = self.get_balls_which_on_field()
        self.assertEqual(0, len(balls_on_field))

    def test_is_game_over(self):
        self.game.field = GameField(1, 1)
        self.game.field.cells[0][0] = 1
        self.assertTrue(self.game.is_game_over())

    def test_get_longest_seq_of_same_balls_horizontal_line(self):
        self.locate_on_playing_field([(1, 0, 1), (1, 1, 1),
                                     (1, 2, 1), (0, 1, 1)])
        result = self.game.get_longest_seq_of_same_balls(1, 1)
        self.assertListEqual([(1, 2), (1, 1), (1, 0)], result)

    def test_get_longest_seq_of_same_balls_diagonal_line(self):
        self.locate_on_playing_field([(1, 1, 1), (2, 2, 1), (3, 3, 1), (4, 4,  1),
                                     (1, 2, 1), (0, 1, 1), (2, 1, 1)])
        result = self.game.get_longest_seq_of_same_balls(1, 1)
        self.assertEqual([(2, 2), (3, 3), (4, 4), (1, 1)], result)

if __name__ == '__main__':
    unittest.main()
