import math


class Vector2D:
    'Represents a 2D vector2D.'
    def __init__(self, x=0, y=0):
        self.x = int(x)
        self.y = int(y)

    def copy(self):
        return Vector2D(self.x, self.y)

    def as_tuple(self):
        return (self.x, self.y)

    def __add__(self, val):
        return Point(self[0] + val[0], self[1] + val[1])

    def __sub__(self, val):
        return Point(self[0] - val[0], self[1] - val[1])

    def __iadd__(self, val):
        self.x = val[0] + self.x
        self.y = val[1] + self.y
        return self

    def __isub__(self, val):
        self.x = self.x - val[0]
        self.y = self.y - val[1]
        return self

    def __div__(self, val):
        return Point(self[0] / val, self[1] / val)

    def __mul__(self, val):
        return Point(self[0] * val, self[1] * val)

    def __idiv__(self, val):
        self[0] = self[0] / val
        self[1] = self[1] / val
        return self

    def __imul__(self, val):
        self[0] = self[0] * val
        self[1] = self[1] * val
        return self

    def __getitem__(self, key):
        if(key == 0):
            return self.x
        elif(key == 1):
            return self.y
        else:
            raise Exception("Invalid key to Point")

    def __setitem__(self, key, value):
        if(key == 0):
            self.x = value
        elif(key == 1):
            self.y = value
        else:
            raise Exception("Invalid key to Point")

    def __hash__(self):
        return ((51 + self.x) * (51 + self.y))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"
Point = Vector2D


def distance_sqrd(point1, point2):
    '''
    Returns the distance between two points squared.
    Marginally faster than Distance()
    '''
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def distance(point1, point2):
    'Returns the distance between two points'
    return math.sqrt(distance_sqrd(point1, point2))


def chess_distance(point1, point2):
    'Returns the chess distance between two points'
    return max(abs(point1.x - point2.x),
               abs(point1.y - point2.y))


def length_sqrd(vec):
    '''
    Returns the length of a vector2D sqaured.
    Faster than Length(), but only marginally
    '''
    return vec[0] ** 2 + vec[1] ** 2


def length(vec):
    'Returns the length of a vector2D'
    return math.sqrt(length_sqrd(vec))


def normalize(vec):
    '''
    Returns a new vector that has the same direction as vec,
    but has a length of one.
    '''
    if(vec[0] == 0. and vec[1] == 0.):
        return Vector2D(0., 0.)
    return vec / length(vec)


def dot(a, b):
    'Computes the dot product of a and b'
    return a[0] * b[0] + a[1] * b[1]


def project_onto(w, v):
    'Projects w onto v.'
    return v * dot(w, v) / length_sqrd(v)


def zero2d():
    return Vector2D(0, 0)


class Rect(object):
    """A rectangle identified by two points.
    The rectangle stores left, top, right, and bottom values."""

    def __init__(self, position, width, height):
        """Initialize a rectangle top left point position and width height."""
        self.set_points(position, width, height)

    def set_points(self, position, width, height):
        """Reset the rectangle coordinates."""
        x, y = position.as_tuple()
        self.left = x
        self.top = y
        self.right = x + width
        self.bottom = y + height

    def contains(self, pt):
        """Return true if a point is inside the rectangle."""
        x, y = pt.as_tuple()
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
        """Return the top-left corner as a Vector2D."""
        return Vector2D(self.left, self.top)

    @property
    def bottom_right(self):
        """Return the bottom-right corner as a Vector2D."""
        return Vector2D(self.right, self.bottom)

    def expanded_by(self, n):
        """Return a rectangle with extended borders.

        Create a new rectangle that is wider and taller than the
        immediate one. All sides are extended by "n" Vector2D.
        """
        p1 = Vector2D(self.left - n, self.top - n)
        p2 = Vector2D(self.right + n, self.bottom + n)
        return Rect(p1, p2)

    def __str__(self):
        return "<Rect (%s, %s) - (%s, %s)>" % (self.left, self.top,
                                               self.right, self.bottom)

    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__,
                               Vector2D(self.left, self.top),
                               Vector2D(self.right, self.bottom))
