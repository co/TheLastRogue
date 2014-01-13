from unittest import TestCase
import direction


class TestSolver(TestCase):

    def test_left_turn_back_returns_right(self):
        left_turn_back = direction.turn_back(direction.LEFT)
        self.assertEqual(left_turn_back, direction.RIGHT)

    def test_down_turn_right_returns_left(self):
        down_turn_right = direction.turn_right(direction.DOWN)
        self.assertEqual(down_turn_right, direction.LEFT)

    def test_left_slight_turn_right_returns_up_left(self):
        print "test1"
        left_turn_slight_right = direction.turn_slight_right(direction.LEFT)
        self.assertEqual(left_turn_slight_right, direction.UP_LEFT)

    def test_up_left_slight_turn_right_returns_up(self):
        print "test2"
        up_left_turn_slight_right = direction.turn_slight_right(direction.UP_LEFT)
        self.assertEqual(up_left_turn_slight_right, direction.UP)

    def test_up_slight_turn_left_returns_up_left(self):
        print "test3"
        up_turn_slight_left = direction.turn_slight_left(direction.UP)
        self.assertEqual(up_turn_slight_left, direction.UP_LEFT)
