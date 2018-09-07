import unittest
from logic import *
from math import sqrt


class TestCalculateDistance(unittest.TestCase):
    def test_same_points(self):
        point1 = Point(5, 5)
        point2 = Point(5, 5)
        result = distance_between_positions(point1, point2)
        self.assertEqual(result, 0)

    def test_dif_points_one(self):
        point1 = Point(0, 0)
        point2 = Point(3, 4)
        result = distance_between_positions(point1, point2)
        self.assertEqual(result, 5)

    def test_dif_points_two(self):
        point1 = Point(5, 2)
        point2 = Point(3, 7)
        result = distance_between_positions(point1, point2)
        self.assertEqual(result, sqrt(29))


class TestPacman(unittest.TestCase):
    def test_pacman_immortality(self):
        game = Game()
        game.cheat('god')
        self.assertEqual(9999, game.pacman.lifes)

    def test_start_position(self):
        game = Game()
        x, y = game.pacman.x, game.pacman.y
        self.assertEqual((x, y), (9, 13))

    def test_default_params(self):
        game = Game()
        x, y = game.pacman.x, game.pacman.y
        game.pacman.next_direction = Direction.up
        game.pacman.current_direction = Direction.right
        for i in range(3):
            game.pacman.move()
        game.pacman.set_default_params()
        self.assertEqual((x, y), (9, 13))
        self.assertEqual(0, game.pacman.scores)
        self.assertEqual(0, game.pacman.eaten_food)
        self.assertEqual(2, game.pacman.lifes)
        self.assertEqual(Direction.left, game.pacman.current_direction)

    def test_movement(self):
        game = Game()
        for i in range(5):
            game.pacman.move()
        game.pacman.next_direction = Direction.up
        game.pacman.move()
        x, y = game.pacman.x, game.pacman.y
        self.assertEqual((x, y), (4, 12))
        self.assertEqual(Direction.up, game.pacman.current_direction)

    def test_eating(self):
        game = Game()
        for i in range(5):
            game.pacman.move()
        self.assertEqual(50, game.pacman.scores)
        self.assertEqual(5, game.pacman.eaten_food)

    def test_items_on_map(self):
        game = Game()
        self.assertTrue(type(game.map[13][9]) is Pacman)
        self.assertTrue(game.map[13][8] is GameMapItem.food)
        self.assertTrue(game.map[12][9] is GameMapItem.wall)
        for i in range(5):
            game.pacman.move()
        self.assertTrue(game.map[13][9] is GameMapItem.empty)
        self.assertTrue(game.map[13][8] is GameMapItem.empty)
        self.assertTrue(game.map[12][9] is GameMapItem.wall)

    def test_clear_ways(self):
        game = Game()
        self.assertTrue(game.pacman.is_clear_way(Direction.left))
        game.pacman.x = 4
        self.assertTrue(not game.pacman.is_clear_way(Direction.left))
        game.pacman.x = 1
        game.pacman.y = 1
        self.assertTrue(not game.pacman.is_clear_way(Direction.up))
        game.pacman.x = 4
        self.assertTrue(game.pacman.is_clear_way(Direction.down))
        game.pacman.x = 0
        game.pacman.y = 8
        self.assertTrue(game.pacman.is_clear_way(Direction.left))
        game.pacman.x = 18
        self.assertTrue(game.pacman.is_clear_way(Direction.right))

    def test_weapon_attack(self):
        game = Game()
        weapon = game.pacman.weapon
        weapon.attack()
        self.assertEqual((weapon.x, weapon.y),
                         (game.pacman.x - 1, game.pacman.y))

    def test_weapon_movement(self):
        game = Game()
        weapon = game.pacman.weapon
        weapon.attack()
        for i in range(4):
            weapon.move()
            self.assertTrue(not weapon.is_dead)
        weapon.move()
        self.assertTrue(weapon.is_dead)

    def test_ghost_killing(self):
        game = Game()
        weapon = game.pacman.weapon
        ghost = game.blinky
        ghost.x, ghost.y = 7, 13
        weapon.attack()
        weapon.move()
        ghost.check_self_death()
        self.assertTrue(ghost.is_dead)

    def test_death(self):
        game = Game()
        ghost, pacman = game.blinky, game.pacman
        ghost.x, ghost.y = 10, 13
        ghost.move()
        self.assertTrue(pacman.is_dead)
        self.assertEqual(1, pacman.lifes)

    def test_blinky_kills_pacman_for_12_steps(self):
        game = Game()
        ghost, pacman = game.blinky, game.pacman
        for i in range(12):
            if i == 10:
                self.assertFalse(pacman.is_dead)
            ghost.move()
        self.assertTrue(pacman.is_dead)


class TestGhost(unittest.TestCase):
    def test_start_position(self):
        game = Game()
        self.assertTrue(game.blinky.x == 9 and game.blinky.y == 7)
        self.assertTrue(game.pinky.x == 9 and game.pinky.y == 8)
        self.assertTrue(game.inky.x == 7 and game.inky.y == 8)
        self.assertTrue(game.clyde.x == 11 and game.clyde.y == 8)

    def test_default_params(self):
        game = Game()
        ghost = game.blinky
        for i in range(5):
            ghost.move()
        self.assertNotEqual(0, ghost.steps)
        ghost.init_start_state()
        self.assertTrue(game.blinky.x == 9 and game.blinky.y == 7)
        self.assertEqual(0, ghost.steps)
        self.assertEqual(Direction.left, ghost.direction)

    def test_exit_from_house(self):
        game = Game()
        game.pacman.eaten_food = 80

        for i in range(1):
            self.assertTrue(game.pinky.in_house)
            game.pinky.move()
        self.assertTrue(not game.pinky.in_house)

        for i in range(3):
            self.assertTrue(game.inky.in_house)
            game.inky.move()
        self.assertTrue(not game.inky.in_house)

        for i in range(3):
            self.assertTrue(game.clyde.in_house)
            game.clyde.move()
        self.assertTrue(not game.clyde.in_house)

    def test_case_of_choosing_worse_way(self):
        game = Game()
        ghost, pacman = game.blinky, game.pacman
        ghost.x, ghost.y = 16, 13
        pacman.x, pacman.y = 15, 17
        ghost.move()
        self.assertEqual(ghost.direction, Direction.down)
        ghost.move()
        ghost.move()
        self.assertEqual(ghost.direction, Direction.left)

    def test_case_of_choosing_better_way(self):
        game = Game()
        ghost, pacman = game.blinky, game.pacman
        ghost.x, ghost.y = 5, 13
        pacman.x, pacman.y = 1, 11
        ghost.move()
        ghost.move()
        self.assertEqual(ghost.direction, Direction.up)

    def test_case_of_choosing_different_ways(self):
        game = Game()
        pinky, blinky, pacman = game.pinky, game.blinky, game.pacman
        pinky.in_house = False
        blinky.x, blinky.y = 16, 13
        pinky.x, pinky.y = 16, 13
        pacman.x, pacman.y = 15, 17
        pacman.current_direction = Direction.right
        for i in range(3):
            blinky.move()
            pinky.move()
        self.assertEqual(blinky.direction, Direction.left)
        self.assertEqual(pinky.direction, Direction.right)


class TestGame(unittest.TestCase):
    def test_making_records_list(self):
        game = Game()
        result = game.get_records_list()
        self.assertEqual(list, type(result))

    def test_updating_records_list(self):
        game = Game()
        game.update_records('TEST', 100)
        result = game.get_records_list()
        self.assertTrue(('TEST', 100) in result)

    def test_cheating(self):
        game = Game()
        game.cheat('level2')
        self.assertNotEqual(1, game.level)
        game.cheat('level3')
        self.assertEqual(3, game.level)

    def test_portals(self):
        game = Game()
        pacman = game.pacman
        pacman.x, pacman.y = 1, 8
        pacman.move()
        pacman.move()
        self.assertEqual((pacman.x, pacman.y), (18, 8))


if __name__ == '__main__':
    unittest.main()

