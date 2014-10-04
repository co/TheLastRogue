import math


def add_2d(point1, point2):
    return point1[0] + point2[0], point1[1] + point2[1]


def sub_2d(point1, point2):
    return point1[0] - point2[0], point1[1] - point2[1]


def int_2d(point):
    return int(point[0]), int(point[1])


def other_side_of_point_direction(point1, point2):
    far_behind_point = sub_2d(point2, point1)
    direction = element_wise_round(normalize(far_behind_point))
    return direction


def other_side_of_point(point1, point2):
    """
    returns the point right behind point2 as seen by point1.
    1 = point1
    2 = point2
    r = result
    ..1..
    .....
    .....
    ...2.
    ...r.
    """
    direction = other_side_of_point_direction(point1, point2)
    return add_2d(point2, direction)


def distance_sqrd(point1, point2):
    """
    Returns the distance between two points squared.
    Marginally faster than Distance()
    """
    return (point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2


def distance(point1, point2):
    """
    Returns the distance between two points
    """
    return math.sqrt(distance_sqrd(point1, point2))


def chess_distance(point1, point2):
    """
    Returns the chess distance between two points
    """
    return max(abs(point1[0] - point2[0]),
               abs(point1[1] - point2[1]))


def length_sqrd(vec):
    """
    Returns the length of a vector2D sqaured.
    Faster than Length(), but only marginally
    """
    return vec[0] ** 2 + vec[1] ** 2


def length(vec):
    'Returns the length of a vector2D'
    return math.sqrt(length_sqrd(vec))


def normalize(point):
    """
    Returns a new vector that has the same direction as vec,
    but has a length of one.
    """
    if(point[0] == 0. and point[1] == 0.):
        return (0., 0.)
    return (point[0] / length(point), point[1] / length(point))


def element_wise_round(point):
    """
    Return new point with each element rounded to nearest int
    """
    return int(round(point[0])), int(round(point[1]))


def dot(a, b):
    """
    Computes the dot product of a and b
    """
    return a[0] * b[0] + a[1] * b[1]


def project_onto(w, v):
    """
    Projects w onto v.
    """
    return v * dot(w, v) / length_sqrd(v)


def zero2d():
    return (0, 0)


class Rect(object):
    """A rectangle identified by two points.
    The rectangle stores left, top, right, and bottom values."""

    def __init__(self, position, width, height):
        """Initialize a rectangle top left point position and width height."""
        self.set_points(position, width, height)

    def set_points(self, position, width, height):
        """Reset the rectangle coordinates."""
        x, y = position
        self.left = x
        self.top = y
        self.right = x + width
        self.bottom = y + height

    def contains(self, pt):
        """Return true if a point is inside the rectangle."""
        x, y = pt
        return (self.left <= x <= self.right and
                self.top <= y <= self.bottom)

    def overlaps(self, other):
        """Return true if a rectangle overlaps this rectangle."""
        return (self.right > other.left and self.left < other.right and
                self.top < other.bottom and self.bottom > other.top)

    @property
    def width(self):
        """Return the width of the rectangle."""
        return self.right - self.left

    @property
    def height(self):
        """Return the height of the rectangle."""
        return self.bottom - self.top

    @property
    def top_left(self):
        """Return the top-left corner as a tuple."""
        return self.left, self.top

    @property
    def bottom_right(self):
        """Return the bottom-right corner as a tuple."""
        return self.right, self.bottom

    def expanded_by(self, point):
        """Return a rectangle with extended borders.

        Create a new rectangle that is wider and taller than the
        immediate one. All sides are extended by "n" tuple.
        """
        p1 = (self.left - point[0], self.top - point[1])
        p2 = (self.right + point[0], self.bottom + point[1])
        return Rect(p1, p2[0] - p1[0], p2[1] - p1[1])

    def containing_points(self):
        result = []
        for x in range(self.left, self.right + 1):
            for y in range(self.top, self.bottom + 1):
                result.append((x, y))
        return result

    def border_points(self):
        result = set()
        for x in range(self.left, self.right + 1):
            result.add((x, self.top))
            result.add((x, self.bottom))
        for y in range(self.top, self.bottom + 1):
            result.add((self.left, y))
            result.add((self.right, y))
        return list(result)

    def __str__(self):
        return "<Rect (%s, %s) - (%s, %s)>" % (self.left, self.top,
                                               self.right, self.bottom)

    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__,
                               (self.left, self.top),
                               (self.right, self.bottom))
