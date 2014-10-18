import unittest
from util import get_path


class TestComposition(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_horizontal_with_same_start_and_destination_is_length_one(self):
        path = get_path((2, 4), (2, 4))
        self.assertEqual(len(path), 1)
        self.assertIn((2, 4), path)

    def test_get_horizontal_path_should_not_contain_no_duplicate_positions(self):
        path = get_path((0, 0), (5, 0))
        self.assertEqual(len(path), 6)
        self.assertEqual((0, 0), path[0])
        self.assertEqual((1, 0), path[1])
        self.assertEqual((2, 0), path[2])
        self.assertEqual((3, 0), path[3])
        self.assertEqual((4, 0), path[4])
        self.assertEqual((5, 0), path[5])
