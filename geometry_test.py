import unittest
from geometry import other_side_of_point_direction, other_side_of_point


class TestComposition(unittest.TestCase):
    def setUp(self):
        pass

    def test_other_side_of_point_direction_should_return_right_when_target_on_left(self):
        """
        1, 2, r
        .....
        .12r.
        .....
        """
        p1 = (-1, 0)
        p2 = (0, 0)
        expected_r = (1, 0)
        self.assertEqual(other_side_of_point_direction(p1, p2), expected_r)

    def test_other_side_of_point_direction_should_return_down_when_target_above(self):
        """
        1, 2, r
        ..1..
        ..2..
        ..r..
        """
        p1 = (0, -1)
        p2 = (0, 0)
        expected_r = (0, 1)
        self.assertEqual(other_side_of_point_direction(p1, p2), expected_r)

    def test_other_side_of_point_direction_should_return_down_left_when_target_up_right(self):
        """
        1, 2, r
        ...1.
        ..2..
        .r...
        """
        p1 = (1, -1)
        p2 = (0, 0)
        expected_r = (-1, 1)
        self.assertEqual(other_side_of_point_direction(p1, p2), expected_r)

    def test_other_side_of_point_direction_should_return_down_left_when_target_up_right(self):
        """
        1, 2, r
        ...1.
        ..2..
        .r...
        """
        p1 = (1, -1)
        p2 = (0, 0)
        expected_r = (-1, 1)
        self.assertEqual(other_side_of_point_direction(p1, p2), expected_r)

    def test_other_side_of_point_should_return_down_when_target_is_up(self):
        """
        1, 2, r
        ...1.
        .....
        .....
        ..2..
        ..r..
        """
        p1 = (1, -3)
        p2 = (0, 0)
        expected_r = (0, 1)
        self.assertEqual(other_side_of_point(p1, p2), expected_r)

    def test_other_side_of_point_should_return_down_left_when_target_up_right(self):
        """
        1, 2, r
        .......1.
        .........
        .........
        ...2.....
        ..r......
        """
        p1 = (4, -3)
        p2 = (0, 0)
        expected_r = (-1, 1)
        self.assertEqual(other_side_of_point(p1, p2), expected_r)
