import math


class Vector2D:
    'Represents a 2D vector2D.'
    def __init__(self, x=0, y=0):
        self.x = int(x)
        self.y = int(y)

    def copy(self):
        return Vector2D(self.x, self.y)

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


def zero():
    return Vector2D(0, 0)
