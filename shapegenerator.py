import random
import rng
import direction
import geometry as geo


def dfs_tunnler(start_position, min_length, max_length,
                size, direction_list):
    position = start_position
    direction_ = random.sample(direction_list, 1)[0]
    visited = set()
    while len(visited) < size:
        direction_ = direction.turn_left_or_right(direction_)
        length = random.randint(min_length, max_length)
        visited.add(position)
        for _ in range(length):
            if(len(visited) >= size):
                break
            position = geo.add_2d(position, direction_)
            visited.add(position)
    return visited


def dfs_tunnler_with_random_stop(start_position, min_length, max_length,
                                 size, direction_list):
    position = start_position
    direction_ = random.sample(direction_list, 1)[0]
    visited = set()
    while len(visited) < size:
        direction_ = direction.turn_left_or_right(direction_)
        length = random.randint(min_length, max_length)
        visited.add(position)
        for _ in range(length):
            if(len(visited) >= size):
                break
            position = geo.add_2d(position, direction_)
            visited.add(position)
        if(rng.coin_flip()):
            position = random.sample(visited, 1)[0]
    return visited


def random_exlosion(start_pos, size, move_list=None):
    if move_list is None:
        move_list = direction.DIRECTIONS
    position = start_pos
    visited = set()
    unvisited_positions = set()
    while len(visited) < size:
        visited.add(position)
        neighbors = set([geo.add_2d(position, _direction)
                         for _direction in move_list])
        unvisited_neighbors = neighbors - visited
        unvisited_positions = unvisited_positions | unvisited_neighbors
        if(len(unvisited_positions) >= 1):
            position = random.sample(unvisited_positions, 1)[0]
        else:
            break
    return visited


class Shape(object):
    def __init__(self, points):
        self._points = set(points)

    @property
    def points(self):
        return self._points

    def calc_rect(self):
        sample_point = random.sample(self.points, 1)[0]
        left = sample_point[0]
        right = sample_point[0]
        up = sample_point[1]
        down = sample_point[1]

        for point in self.points:
            left = min(point[0], left)
            right = max(point[0], right)
            up = min(point[1], up)
            down = max(point[1], down)
        return geo.Rect((left, up), right - left, down - up)

    def calc_normalized_points(self, offset=0):
        rect = self.calc_rect()
        normalized = set()
        for point in self.points:
            normalized.add((point[0] - rect.left + offset,
                            point[1] - rect.top + offset))
        return normalized
