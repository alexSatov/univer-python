import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))

from logic import Game, Bot, ABot, BoardCell


class TGame:
    def __init__(self, settings_index):
        test_files = ['settings.txt', 'settings1.txt',
                      'settings2.txt', 'settings3.txt']
        self.game = Game(test_files[settings_index])


class TestSimpleFunctions(unittest.TestCase):
    def test_cell_on_board(self):
        game = TGame(1).game
        self.assertTrue(game.cell_on_board(0, 0))
        self.assertTrue(game.cell_on_board(5, 4))
        self.assertFalse(game.cell_on_board(-1, -1))
        self.assertFalse(game.cell_on_board(-1, 4))
        self.assertFalse(game.cell_on_board(3, 10))

    def test_active_player(self):
        game = TGame(1).game
        self.assertTrue(game.active_player.checkers_type
                        is BoardCell.fp_checker)
        game.is_first_player_move = False
        self.assertTrue(game.active_player.checkers_type
                        is BoardCell.sp_checker)

    def test_start_new_game(self):
        game = TGame(1).game
        begin_count = game.active_player.checkers_count

        game.clean_board()
        self.assertEqual(0, game.active_player.checkers_count)

        game.start_new_game()
        end_count = game.active_player.checkers_count
        self.assertEqual(begin_count, end_count)

    def test_game_over(self):
        game = TGame(1).game
        game.clean_board()
        game.check_game_over()
        self.assertTrue(game.is_over)

    def test_change_player(self):
        game = TGame(1).game
        self.assertTrue(game.first_player.should_make_move)
        game.change_player()
        self.assertTrue(game.second_player.should_make_move)

    def test_active_checker(self):
        game = TGame(1).game
        checker = game.board[7][2]
        game.try_activate(checker)
        result = game.active_player.active_checker
        self.assertEqual(checker, result)

    def test_deactivation(self):
        game = TGame(1).game
        checker = game.board[7][2]
        game.try_activate(checker)
        self.assertTrue(checker.is_active)
        checker.deactivate()
        self.assertFalse(checker.is_active)


class TestSimpleActions(unittest.TestCase):
    def test_initialization(self):
        game = TGame(1).game
        board = game.board
        white_checker = board[7][2]
        black_checker = board[7][4]

        self.assertTrue(game.is_first_player_move)
        self.assertEqual(white_checker.type, BoardCell.fp_checker)
        self.assertEqual(black_checker.type, BoardCell.sp_checker)

    def test_activation_first(self):
        game = TGame(1).game
        board = game.board
        white_checker = board[7][2]
        black_checker = board[7][4]
        blocked_white_checker = board[4][9]

        game.try_activate(black_checker)
        self.assertFalse(black_checker.is_active)

        game.try_activate(blocked_white_checker)
        self.assertFalse(blocked_white_checker.is_active)

        game.try_activate(white_checker)
        self.assertTrue(white_checker.is_active)
        game.try_activate(white_checker)
        self.assertFalse(white_checker.is_active)

    def test_activation_second(self):
        game = TGame(1).game
        board = game.board
        first_white_checker = board[7][2]
        second_white_checker = board[6][7]

        game.try_activate(first_white_checker)
        game.try_activate(second_white_checker)

        self.assertFalse(first_white_checker.is_active)
        self.assertTrue(second_white_checker.is_active)

    def test_move(self):
        game = TGame(1).game
        board = game.board
        checker = board[7][2]

        game.try_activate(checker)
        game.active_player.make_move(6, 1)

        self.assertEqual((checker.y, checker.x), (6, 1))
        self.assertTrue(board[7][2] is BoardCell.empty)

    def test_player_change(self):
        game = TGame(1).game
        board = game.board
        checker = board[7][2]

        self.assertTrue(game.first_player.should_make_move)

        game.try_activate(checker)
        game.active_player.make_move(6, 1)

        self.assertTrue(game.second_player.should_make_move)

    def test_necessarily_cut(self):
        game = TGame(1).game
        board = game.board
        white_checker = board[7][2]
        black_checker_move = board[8][5]

        game.try_activate(white_checker)
        game.active_player.make_move(6, 3)

        game.try_activate(black_checker_move)
        self.assertFalse(black_checker_move.is_active)
        self.assertTrue(game.second_player.must_cut())

    def test_cut(self):
        game = TGame(1).game
        board = game.board
        white_checker = board[7][2]
        black_checker_cut = board[7][4]

        game.try_activate(white_checker)
        game.active_player.make_move(6, 3)

        game.try_activate(black_checker_cut)
        self.assertTrue(black_checker_cut.is_active)
        self.assertTrue(board[5][2] is BoardCell.checker_move)

        game.active_player.make_move(5, 2)
        self.assertEqual((black_checker_cut.y, black_checker_cut.x), (5, 2))
        self.assertTrue(board[6][3] is BoardCell.empty)
        self.assertTrue(game.is_first_player_move)

    def test_back_cut(self):
        game = TGame(1).game
        board = game.board
        white_checker = board[7][2]
        black_checker = board[7][4]

        game.is_first_player_move = False
        game.try_activate(black_checker)
        game.active_player.make_move(8, 3)

        game.try_activate(white_checker)
        game.active_player.make_move(9, 4)

        self.assertEqual((white_checker.y, white_checker.x), (9, 4))
        self.assertTrue(board[7][2] is BoardCell.empty)
        self.assertTrue(board[7][4] is BoardCell.empty)
        self.assertTrue(board[8][3] is BoardCell.empty)


class TestActions(unittest.TestCase):
    def test_multiple_cut(self):
        game = TGame(1).game
        board = game.board
        white_checker = board[2][1]
        black_checker = board[0][3]

        game.is_first_player_move = False
        game.try_activate(black_checker)
        game.active_player.make_move(1, 4)

        game.try_activate(white_checker)
        game.active_player.make_move(0, 3)
        self.assertFalse(game.first_player.last_cut)
        self.assertTrue(game.first_player.must_cut())
        self.assertTrue(game.is_first_player_move)
        self.assertTrue(white_checker.can_cut)
        self.assertFalse(white_checker.is_active)

        game.try_activate(white_checker)
        game.active_player.make_move(2, 5)
        self.assertTrue(game.first_player.last_cut)
        self.assertFalse(game.is_first_player_move)

        self.assertEqual((white_checker.y, white_checker.x), (2, 5))
        self.assertTrue(board[1][2] is BoardCell.empty)
        self.assertTrue(board[1][4] is BoardCell.empty)

    def test_multiple_cut_choice(self):
        game = TGame(1).game
        board = game.board
        white_checker = board[4][9]
        black_checker = board[2][7]

        game.is_first_player_move = False
        game.try_activate(black_checker)
        game.active_player.make_move(3, 6)

        game.try_activate(white_checker)
        game.active_player.make_move(2, 7)
        game.try_activate(white_checker)

        self.assertFalse(game.first_player.last_cut)
        self.assertTrue(white_checker.cutting)
        self.assertTrue(board[4][5] is BoardCell.checker_move)
        self.assertTrue(board[0][9] is BoardCell.checker_move)


class TestQueenActions(unittest.TestCase):
    def test_transformation_simple(self):
        game = TGame(1).game
        board = game.board
        black_checker = board[8][5]

        game.is_first_player_move = False
        game.try_activate(black_checker)
        game.active_player.make_move(9, 4)

        self.assertTrue(black_checker.is_queen)

    def test_transformation_after_multiple_cut(self):
        game = TGame(1).game
        board = game.board
        white_checker = board[4][9]
        black_checker = board[2][7]

        game.is_first_player_move = False
        game.try_activate(black_checker)
        game.active_player.make_move(1, 6)

        game.try_activate(white_checker)
        game.active_player.make_move(2, 7)
        game.try_activate(white_checker)
        game.active_player.make_move(0, 9)

        self.assertTrue(white_checker.is_queen)

    def test_not_transformation_after_multiple_cut(self):
        game = TGame(1).game
        board = game.board
        white_checker = board[2][1]
        black_checker = board[0][3]

        game.is_first_player_move = False
        game.try_activate(black_checker)
        game.active_player.make_move(1, 4)

        game.try_activate(white_checker)
        game.active_player.make_move(0, 3)
        game.try_activate(white_checker)
        game.active_player.make_move(2, 5)

        self.assertFalse(white_checker.is_queen)

    def test_stop_multiple_cut_after_transformation(self):
        game = TGame(1).game
        board = game.board
        white_checker = board[4][9]
        black_checker = board[2][7]

        game.is_first_player_move = False
        game.try_activate(black_checker)
        game.active_player.make_move(1, 6)

        game.try_activate(white_checker)
        game.active_player.make_move(2, 7)
        game.try_activate(white_checker)
        game.active_player.make_move(0, 5)

        self.assertTrue(white_checker.is_queen)
        self.assertFalse(game.is_first_player_move)

        game.try_activate(white_checker)
        self.assertFalse(white_checker.is_active)

    def test_correct_move_activation(self):
        game = TGame(1).game
        board = game.board
        black_checker = board[8][5]
        board[7][4] = BoardCell.empty
        board[7][8] = BoardCell.empty

        game.is_first_player_move = False
        game.try_activate(black_checker)
        game.active_player.make_move(9, 6)
        game.is_first_player_move = False
        game.try_activate(black_checker)

        self.assertTrue(board[8][7] is BoardCell.checker_move)
        for i in range(1, 6):
            self.assertTrue(board[9-i][6-i] is BoardCell.checker_move)

    def test_correct_cut_activation_first(self):
        game = TGame(1).game
        board = game.board
        white_checker = board[1][0]

        game.try_activate(white_checker)
        game.active_player.make_move(0, 1)
        game.is_first_player_move = True
        game.try_activate(white_checker)

        self.assertFalse(white_checker.can_cut())
        self.assertFalse(board[3][4] is BoardCell.checker_move)

    def test_correct_cut_activation_second(self):
        game = TGame(1).game
        board = game.board
        white_checker = board[1][0]
        board[2][3] = BoardCell.empty

        game.try_activate(white_checker)
        game.active_player.make_move(0, 1)
        game.is_first_player_move = True
        game.try_activate(white_checker)

        self.assertTrue(white_checker.can_cut())

        for i in range(1, 5):
            self.assertTrue(board[1+i][2+i] is BoardCell.checker_move)

    def test_necessarily_cut(self):
        game = TGame(1).game
        board = game.board
        black_checker = board[8][5]
        board[7][4] = BoardCell.empty

        game.is_first_player_move = False
        game.try_activate(black_checker)
        game.active_player.make_move(9, 6)
        game.is_first_player_move = False
        game.try_activate(black_checker)

        self.assertTrue(game.second_player.must_cut())
        self.assertTrue(board[6][9] is BoardCell.checker_move)

    def test_free_long_cut(self):
        game = TGame(1).game
        board = game.board
        white_checkers_count_begin = game.first_player.checkers_count
        black_checker = board[8][5]

        game.is_first_player_move = False
        game.try_activate(black_checker)
        game.active_player.make_move(9, 6)
        game.is_first_player_move = False
        game.try_activate(black_checker)
        game.active_player.make_move(6, 9)
        game.try_activate(black_checker)
        game.active_player.make_move(3, 6)
        game.try_activate(black_checker)
        game.active_player.make_move(8, 1)

        white_checkers_count_end = game.first_player.checkers_count

        self.assertTrue(white_checkers_count_begin -
                        white_checkers_count_end == 3)


class TestBot(unittest.TestCase):
    def test_bot_move(self):
        game = TGame(2).game

        player_checker = game.board[8][7]
        bot_checker = game.board[6][9]
        self.assertEqual(type(bot_checker.player), Bot)

        game.try_activate(player_checker)
        game.active_player.make_move(7, 6)

        self.assertEqual(type(game.active_player), Bot)
        game.active_player.choose_move()  # Bot makes move

        self.assertEqual(game.board[6][9], BoardCell.empty)
        self.assertEqual(game.board[7][8], bot_checker)

    def test_bot_cut(self):
        game = TGame(2).game

        player_checker = game.board[8][7]
        bot_checker = game.board[6][9]

        game.try_activate(player_checker)
        game.active_player.make_move(7, 8)

        self.assertTrue(game.active_player.must_cut())
        game.active_player.choose_move()  # Bot makes cut

        self.assertEqual(game.board[6][9], BoardCell.empty)
        self.assertEqual(game.board[7][8], BoardCell.empty)
        self.assertEqual(game.board[8][7], bot_checker)
        self.assertFalse(player_checker in game.first_player.checkers)

    def test_bot_queen_cut(self):
        game = TGame(2).game

        player_checker = game.board[8][7]
        bot_checker = game.board[6][9]

        game.try_activate(player_checker)
        game.active_player.make_move(7, 8)
        game.active_player.choose_move()
        player_checker = game.board[7][4]
        game.try_activate(player_checker)
        game.active_player.make_move(6, 3)
        game.active_player.choose_move()
        self.assertTrue(bot_checker.is_queen, True)
        game.try_activate(player_checker)
        game.active_player.make_move(5, 2)
        game.active_player.choose_move()  # Bot makes queen cut

        self.assertEqual(game.board[5][2], BoardCell.empty)
        self.assertEqual(game.board[9][6], BoardCell.empty)
        self.assertEqual(game.board[4][1], bot_checker)
        self.assertFalse(player_checker in game.first_player.checkers)

    def test_bot_multiple_cut(self):
        game = TGame(2).game

        player_checker = game.board[7][2]
        bot_checker = game.board[5][0]
        start_checkers_count = game.first_player.checkers_count

        game.try_activate(player_checker)
        game.active_player.make_move(6, 3)
        game.active_player.choose_move()  # Bot makes first cut

        self.assertEqual(type(game.active_player), Bot)
        self.assertTrue(game.active_player.must_cut())
        self.assertFalse(game.active_player.last_cut)
        self.assertTrue(bot_checker.cutting)

        game.active_player.choose_move()  # Bot makes second cut
        end_checkers_count = game.first_player.checkers_count

        self.assertEqual(game.board[7][2], BoardCell.empty)
        self.assertEqual(game.board[5][0], BoardCell.empty)
        self.assertEqual(game.board[6][1], BoardCell.empty)
        self.assertEqual(game.board[5][4], bot_checker)
        self.assertEqual(start_checkers_count - end_checkers_count, 2)


class TestAdvancedBot(unittest.TestCase):
    def test_bot_save_move(self):
        game = TGame(3).game

        player_checker = game.board[8][1]
        bot_checker = game.board[5][0]
        self.assertEqual(type(bot_checker.player), ABot)

        game.try_activate(player_checker)
        game.active_player.make_move(7, 2)
        game.try_activate(bot_checker)
        game.active_player.make_move(6, 1)
        self.assertTrue(game.first_player.must_cut())  # Example of bad move

        game.move_back()

        for i in range(10):
            game.second_player.choose_move()
            self.assertFalse(game.first_player.must_cut())
            game.move_back()  # ABot always choosing save move

    def test_bot_cut(self):
        game = TGame(3).game

        player_checker = game.board[8][1]
        bot_checker = game.board[5][4]

        game.try_activate(player_checker)
        game.active_player.make_move(7, 2)
        game.active_player.choose_move()
        player_checker = game.board[8][5]
        game.try_activate(player_checker)
        game.active_player.make_move(7, 6)
        game.active_player.choose_move()  # ABot makes cut

        self.assertEqual(game.board[6][9], BoardCell.empty)
        self.assertEqual(game.board[7][8], BoardCell.empty)
        self.assertEqual(game.board[8][7], bot_checker)
        self.assertFalse(player_checker in game.first_player.checkers)

    def test_bot_queen_cut(self):
        game = TGame(3).game

        player_checker = game.board[8][1]
        bot_checker = game.board[8][9]

        game.try_activate(player_checker)
        game.active_player.make_move(7, 2)
        game.active_player.choose_move()
        player_checker = game.board[9][8]
        game.try_activate(player_checker)
        game.active_player.make_move(8, 7)
        game.active_player.choose_move()
        self.assertTrue(bot_checker.is_queen, True)
        player_checker = game.board[8][5]
        game.try_activate(player_checker)
        game.active_player.make_move(7, 4)
        game.active_player.choose_move()  # ABot makes queen cut

        self.assertEqual(game.board[9][8], BoardCell.empty)
        self.assertEqual(game.board[8][7], BoardCell.empty)
        self.assertEqual(game.board[7][6], bot_checker)

    def test_bot_multiple_cut(self):
        game = TGame(3).game

        player_checker = game.board[8][1]
        bot_checker = game.board[5][4]
        start_checkers_count = game.first_player.checkers_count

        game.try_activate(player_checker)
        game.active_player.make_move(7, 2)
        game.active_player.choose_move()
        player_checker = game.board[8][3]
        game.try_activate(player_checker)
        game.active_player.make_move(7, 4)
        game.active_player.choose_move()  # Bot makes first cut

        self.assertEqual(type(game.active_player), ABot)
        self.assertTrue(game.active_player.must_cut())
        self.assertFalse(game.active_player.last_cut)
        self.assertTrue(bot_checker.cutting)

        game.active_player.choose_move()  # Bot makes second cut
        end_checkers_count = game.first_player.checkers_count

        self.assertEqual(game.board[7][2], BoardCell.empty)
        self.assertEqual(game.board[7][4], BoardCell.empty)
        self.assertEqual(game.board[6][5], BoardCell.empty)
        self.assertEqual(game.board[6][1], bot_checker)
        self.assertEqual(start_checkers_count - end_checkers_count, 2)


if __name__ == '__main__':
    unittest.main()
