from enum import IntEnum
from random import randint
from settings import GameSettings
from collections import namedtuple


Cell = namedtuple('Cell', ['y', 'x'])
Move = namedtuple('Move', ['checker', 'cell'])
State = namedtuple('State', ['moved_checker', 'cell', 'prev_cell', 'is_queen',
                             'felled_checker', 'which_player'])

cells_to_check = [Cell(-1, -1), Cell(-1, 1), Cell(1, -1), Cell(1, 1)]


class BoardCell(IntEnum):
    empty = 0
    fp_checker = 1  # first player
    sp_checker = 2  # second player
    checker_move = 3


class Game:
    def __init__(self, settings_file=''):
        self.board = []
        self.states = []
        self.settings = GameSettings() if settings_file == '' else \
            GameSettings(settings_file)
        self.board_size = self.settings.board_size
        self.init_board()
        self.is_over = False
        self.is_first_player_move = True
        self.first_player = self.set_player(BoardCell.fp_checker)
        self.second_player = self.set_player(BoardCell.sp_checker)

    @property
    def active_player(self):
        return self.first_player if self.is_first_player_move else \
            self.second_player

    @property
    def active_moves(self):
        moves = []
        for y in range(self.board_size):
            for x in range(self.board_size):
                if self.board[y][x] == BoardCell.checker_move:
                    moves.append(Cell(y, x))
        return moves

    def set_player(self, checkers_type):
        player_name = self.settings.player1 \
            if checkers_type == BoardCell.fp_checker else self.settings.player2
        if player_name == 'player':
            return Player(self, checkers_type)
        if player_name == 'bot':
            return Bot(self, checkers_type)
        if player_name == 'abot':
            return ABot(self, checkers_type)

    def cell_on_board(self, y, x):
        return 0 <= y < self.board_size and 0 <= x < self.board_size

    def clean_board(self):
        for y in range(self.board_size):
            for x in range(self.board_size):
                self.board[y][x] = BoardCell.empty

    def init_board(self):
        if self.settings.config == 'classic':
            self.init_classic_board()
        elif self.settings.config == 'frisian':
            self.init_frisian_board()
        else:
            self.init_board_from_file(self.settings.config)

    def init_classic_board(self):
        odd = lambda i, j: (i + j) % 2 == 1
        for y in range(self.board_size):
            self.board.append([])
            for x in range(self.board_size):
                if 0 <= y < self.board_size / 2 - 1 and odd(y, x):
                    self.board[y].append(Checker(self, y, x,
                                                 BoardCell.sp_checker))
                elif self.board_size / 2 < y < self.board_size and odd(y, x):
                    self.board[y].append(Checker(self, y, x,
                                                 BoardCell.fp_checker))
                else:
                    self.board[y].append(BoardCell.empty)

    def init_frisian_board(self):
        for y in range(self.board_size):
            self.board.append([])
            for x in range(self.board_size):
                if 0 <= y < self.board_size / 2 - 1:
                    self.board[y].append(Checker(self, y, x,
                                                 BoardCell.sp_checker))
                elif self.board_size / 2 < y < self.board_size:
                    self.board[y].append(Checker(self, y, x,
                                                 BoardCell.fp_checker))
                else:
                    self.board[y].append(BoardCell.empty)

    def init_board_from_file(self, file):
        try:
            with open(file) as file:
                y = 0
                for row in file:
                    self.board.append([])
                    x = 0
                    for cell in row:
                        if cell == '\n':
                            continue
                        if cell == '0':
                            self.board[y].append(BoardCell(int(cell)))
                        else:
                            self.board[y].append(Checker(self, y, x,
                                                         BoardCell(int(cell))))
                        x += 1
                    y += 1
                self.board_size = y
                self.settings.board_size = self.board_size
                self.settings.save()
        except FileNotFoundError or FileExistsError:
            print('Incorrect config file name')
            exit()

    def start_new_game(self):
        self.board = []
        self.init_board()
        self.is_over = False
        self.is_first_player_move = True

    def change_player(self):
        self.is_first_player_move = not self.is_first_player_move

    def try_activate(self, selected_checker):
        if self.active_player.checkers_type == selected_checker.type:
            if selected_checker.is_active:
                selected_checker.deactivate()
            else:
                for checker in self.active_player.checkers:
                    if checker.is_active:
                        checker.deactivate()

                if self.active_player.must_cut():
                    if not self.active_player.last_cut:
                        if selected_checker.cutting:
                            selected_checker.is_active = True
                            selected_checker.activate_cutting_moves()
                    elif selected_checker.can_cut():
                        selected_checker.is_active = True
                        selected_checker.activate_cutting_moves()
                elif selected_checker.is_free_move():
                    selected_checker.is_active = True
                    selected_checker.activate_moves()

    def check_game_over(self):
        self.is_over = True
        for checker in self.active_player.checkers:
            if checker.is_free_move() or checker.can_cut():
                self.is_over = False
                break

    def move_back(self):
        if len(self.states) > 0:
            state = self.states.pop()

            if state.felled_checker is not None:
                y, x = state.felled_checker.y, state.felled_checker.x
                self.board[y][x] = state.felled_checker

            y, x = state.cell.y, state.cell.x
            self.board[state.moved_checker.y][state.moved_checker.x] = \
                BoardCell.empty

            state.moved_checker.y, state.moved_checker.x = y, x
            state.moved_checker.is_queen = state.is_queen
            state.moved_checker.previous_cell = state.prev_cell
            self.board[y][x] = state.moved_checker
            self.is_first_player_move = state.which_player


class Checker:
    def __init__(self, game, y, x, checker_type):
        self.x = x
        self.y = y
        self.game = game
        self.cutting = False
        self.is_queen = False
        self.is_active = False
        self.type = checker_type
        self.previous_cell = None

    @property
    def player(self):
        return self.game.first_player if self.type == BoardCell.fp_checker \
            else self.game.second_player

    def deactivate(self):
        self.is_active = False
        self.clean_moves()

    def is_enemy_checker(self, checker):
        try:
            return checker.type != self.type
        except IndexError:
            return False

    def is_empty_cell(self, y, x):
        try:
            return not isinstance(self.game.board[y][x], Checker)
        except IndexError:
            return False

    def is_free_move(self):
        moves = []
        moves = self.check_queen_moves(moves) if self.is_queen \
            else self.check_simple_moves(moves)

        for move in moves:
            if move == BoardCell.empty:
                return True
        return False

    def check_simple_moves(self, moves):
        dy = -1 if self.type == BoardCell.fp_checker else 1
        dy += self.y

        if 0 <= self.x - 1 < self.game.board_size:
            dx = self.x - 1
            moves.append(self.game.board[dy][dx])

        if 0 <= self.x + 1 < self.game.board_size:
            dx = self.x + 1
            moves.append(self.game.board[dy][dx])

        return moves

    def check_queen_moves(self, moves):
        for cell in cells_to_check:
            dy = self.y + cell.y
            dx = self.x + cell.x
            if self.game.cell_on_board(dy, dx):
                moves.append(self.game.board[dy][dx])
        return moves

    def activate_moves(self):
        moves = []
        moves = self.activate_queen_moves(moves) if self.is_queen \
            else self.activate_simple_moves(moves)

        for move in moves:
            if self.is_empty_cell(move.y, move.x):
                self.game.board[move.y][move.x] = BoardCell.checker_move

    def activate_simple_moves(self, moves):
        dy = -1 if self.type == BoardCell.fp_checker else 1
        dy += self.y

        if 0 <= self.x - 1 < self.game.board_size:
            dx = self.x - 1
            moves.append(Cell(dy, dx))

        if 0 <= self.x + 1 < self.game.board_size:
            dx = self.x + 1
            moves.append(Cell(dy, dx))

        return moves

    def activate_queen_moves(self, moves):
        for cell in cells_to_check:
            dy, dx = self.y + cell.y, self.x + cell.x

            while self.is_empty_cell(dy, dx) and \
                    self.game.cell_on_board(dy, dx):
                moves.append(Cell(dy, dx))
                dy += cell.y
                dx += cell.x

        return moves

    def can_cut(self):
        return self.check_queen_cut() if self.is_queen \
            else self.check_simple_cut()

    def check_simple_cut(self):
        for cell in cells_to_check:
            dy, dx = self.y + cell.y, self.x + cell.x

            if self.game.cell_on_board(dy + cell.y, dx + cell.x):
                if isinstance(self.game.board[dy][dx], Checker):
                    checker = self.game.board[dy][dx]
                    if self.is_enemy_checker(checker) and \
                            self.is_empty_cell(dy + cell.y, dx + cell.x):
                        return True
        return False

    def check_queen_cut(self):
        for cell in cells_to_check:
            dy, dx = self.y + cell.y, self.x + cell.x

            while self.game.cell_on_board(dy + cell.y, dx + cell.x):
                if Cell(dy, dx) == self.previous_cell:
                    self.previous_cell = None
                    break

                if isinstance(self.game.board[dy][dx], Checker):
                    checker = self.game.board[dy][dx]
                    if self.is_enemy_checker(checker) and \
                            self.is_empty_cell(dy + cell.y, dx + cell.x):
                        return True
                    break

                dy += cell.y
                dx += cell.x

        return False

    def activate_cutting_moves(self):
        self.activate_queen_cutting_moves() if self.is_queen else \
            self.activate_simple_cutting_moves()

    def activate_simple_cutting_moves(self):
        for cell in cells_to_check:
            dy, dx = self.y + cell.y, self.x + cell.x
            if self.game.cell_on_board(dy + cell.y, dx + cell.x):
                if isinstance(self.game.board[dy][dx], Checker):
                    checker = self.game.board[dy][dx]
                    if self.is_enemy_checker(checker) and \
                            self.is_empty_cell(dy + cell.y, dx + cell.x):
                        dy += cell.y
                        dx += cell.x
                        self.game.board[dy][dx] = BoardCell.checker_move

    def activate_queen_cutting_moves(self):
        for cell in cells_to_check:
            dy, dx = self.y + cell.y, self.x + cell.x

            while self.game.cell_on_board(dy + cell.y, dx + cell.x):
                if isinstance(self.game.board[dy][dx], Checker):
                    checker = self.game.board[dy][dx]
                    if self.is_enemy_checker(checker) and \
                            self.is_empty_cell(dy + cell.y, dx + cell.x):
                        while self.is_empty_cell(dy+cell.y, dx+cell.x) and \
                                self.game.cell_on_board(dy + cell.y,
                                                        dx + cell.x):
                            dy += cell.y
                            dx += cell.x
                            self.game.board[dy][dx] = BoardCell.checker_move
                    break
                dy += cell.y
                dx += cell.x

    def clean_moves(self):
        for y in range(self.game.board_size):
            for x in range(self.game.board_size):
                if self.game.board[y][x] == BoardCell.checker_move:
                    self.game.board[y][x] = BoardCell.empty

    def check_queen_state(self):
        white_on_top_line = self.y == 0 and self.type == BoardCell.fp_checker
        black_on_bottom_line = self.y == self.game.board_size - 1 and \
            self.type == BoardCell.sp_checker

        if (white_on_top_line or black_on_bottom_line) and not self.cutting:
            self.is_queen = True


class Player:
    def __init__(self, game, checkers_type):
        self.game = game
        self.max_depth = 3
        self.last_cut = True
        self.best_move = None
        self.checkers_type = checkers_type

    @property
    def enemy(self):
        return self.game.second_player \
            if self.checkers_type is BoardCell.fp_checker \
            else self.game.first_player

    @property
    def checkers(self):
        return self.get_all_checkers(self.checkers_type)

    @property
    def checkers_to_move(self):
        return [checker for checker in self.checkers if checker.is_free_move()]

    @property
    def checkers_to_cut(self):
        checkers = []

        for checker in self.checkers:
            if checker.cutting:
                return [checker]
            if checker.can_cut():
                checkers.append(checker)

        return checkers

    @property
    def should_make_move(self):
        return (self.checkers_type == BoardCell.fp_checker and
                self.game.is_first_player_move) or \
               (self.checkers_type == BoardCell.sp_checker and not
                self.game.is_first_player_move)

    @property
    def checkers_count(self):
        return len(self.checkers)

    @property
    def active_checker(self):
        try:
            return [checker for checker in self.checkers if checker.is_active]\
                   .pop()
        except IndexError:
            return None

    def get_all_moves(self):
        return self.gather_moves(step_moves=False) if self.must_cut() else \
            self.gather_moves()

    def gather_moves(self, step_moves=True):
        moves = []
        checkers = self.checkers_to_move if step_moves else \
            self.checkers_to_cut
        for checker in checkers:
            self.game.try_activate(checker)
            move_cells = self.game.active_moves
            checker.deactivate()
            for move_cell in move_cells:
                moves.append(Move(checker, move_cell))
        return moves

    def choose_move(self):
        pass

    def make_move(self, y, x):
        self.cut(y, x) if self.active_checker.can_cut() else self.move(y, x)

    def move(self, y, x):
        move_checker = self.active_checker
        current_cell = Cell(move_checker.y, move_checker.x)
        self.game.states.append(State(move_checker, current_cell,
                                      move_checker.previous_cell,
                                      move_checker.is_queen, None,
                                      self.game.is_first_player_move))

        move_checker.previous_cell = current_cell
        self.game.board[move_checker.y][move_checker.x] = BoardCell.empty
        self.game.board[y][x] = move_checker
        move_checker.y, move_checker.x = y, x

        self.finish_move(move_checker)

    def cut(self, y, x):
        cut_checker = self.active_checker
        current_cell = Cell(cut_checker.y, cut_checker.x)
        self.game.board[cut_checker.y][cut_checker.x] = BoardCell.empty
        self.game.board[y][x] = cut_checker

        dy, dx = cut_checker.y - y, cut_checker.x - x
        dy, dx = dy // abs(dy), dx // abs(dx)

        while (y + dy, x + dx) != (cut_checker.y, cut_checker.x):

            if isinstance(self.game.board[y + dy][x + dx], Checker):
                felled_checker = self.game.board[y + dy][x + dx]
                self.game.states.append(State(cut_checker, current_cell,
                                              cut_checker.previous_cell,
                                              cut_checker.is_queen,
                                              felled_checker,
                                              self.game.is_first_player_move))

            self.game.board[y + dy][x + dx] = BoardCell.empty
            dx += dx // abs(dx)
            dy += dy // abs(dy)

        cut_checker.previous_cell = current_cell
        cut_checker.y, cut_checker.x = y, x
        cut_checker.deactivate()
        cut_checker.cutting = cut_checker.can_cut()

        if not cut_checker.cutting:
            self.last_cut = True
            self.finish_move(cut_checker)
        else:
            self.last_cut = False

    def finish_move(self, checker):
        checker.check_queen_state()
        checker.deactivate()
        self.game.change_player()
        self.game.check_game_over()

    def must_cut(self):
        if not self.last_cut:
            return True
        for checker in self.checkers:
            if checker.can_cut():
                return True
        return False

    def get_all_checkers(self, checkers_type):
        checkers = []
        for y in range(self.game.board_size):
            for x in range(self.game.board_size):
                if isinstance(self.game.board[y][x], Checker):
                    if self.game.board[y][x].type == checkers_type:
                        checkers.append(self.game.board[y][x])
        return checkers

    def search_best_move(self, depth):
        balance = -1000
        if depth == 0:
            return self.evaluate()

        moves = self.get_all_moves()
        if len(moves) == 0:
            return -1

        while len(moves) > 0:
            moves_count = 1
            move = moves.pop()
            self.game.try_activate(move.checker)
            self.make_move(move.cell.y, move.cell.x)
            while not self.last_cut:
                cut_move = self.get_all_moves()[0]
                self.game.try_activate(cut_move.checker)
                self.make_move(cut_move.cell.y, cut_move.cell.x)
                moves_count += 1

            current_balance = -self.enemy.search_best_move(depth - 1)
            if current_balance >= balance:
                rand_k = 1
                if current_balance == balance:
                    rand_k = randint(0, 1)
                if rand_k == 1:
                    if depth == self.max_depth:
                        self.best_move = move
                    balance = current_balance

            for i in range(moves_count):
                self.game.move_back()

        return balance

    def evaluate(self):
        return self.checkers_count - self.enemy.checkers_count


class Bot(Player):
    def __init__(self, game, checkers_type):
        super().__init__(game, checkers_type)

    def choose_move(self):
        checker = self.choose_checker()
        self.game.try_activate(checker)
        moves = self.game.active_moves
        move = moves[randint(0, len(moves)) - 1]
        self.make_move(move.y, move.x)

    def choose_checker(self):
        checkers = self.checkers_to_cut if self.must_cut() else \
            self.checkers_to_move
        return checkers[randint(0, len(checkers)) - 1]


class ABot(Bot):  # Advanced Bot
    def __init__(self, game, checkers_type):
        super().__init__(game, checkers_type)

    def choose_move(self):
        self.search_best_move(self.max_depth)
        move = self.best_move
        self.game.try_activate(move.checker)
        self.make_move(move.cell.y, move.cell.x)