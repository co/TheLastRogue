class Graph(object):
    def __init__(self):
        self._points = {}
        self._edges = set()

    def add_point(self, point):
        self._points[point] = Vertex(point)

    def add_edge(self, point1, point2):
        self._points[point1].add_neighbor(self._points[point2])
        self._points[point2].add_neighbor(self._points[point1])
        self._edges.add(frozenset([point1, point2]))

    def has_point(self, point):
        return point in self._points

    def has_edge(self, point1, point2):
        return frozenset([point1, point2]) in self._edges

    def is_connected(self):
        if len(self._points) < 1:
            return True
        first = self._points.values()[0]
        visited = set()
        visited.add(first)
        next_to_visit = set(first.get_neighbors())
        while len(next_to_visit) > 0:
            current_point = next_to_visit.pop()
            visited.add(current_point)
            next_to_visit.update(set(current_point.get_neighbors()) - visited)
        return len(self._points) == len(visited)


class Vertex(object):
# Payload also serves as identifier
    def __init__(self, payload):
        self._payload = payload
        self._neighbors = set()

    @property
    def payload(self):
        return self._payload

    def add_neighbor(self, neighbor):
        self._neighbors.add(neighbor)

    def get_neighbors(self):
        return list(self._neighbors)

    def __hash__(self):
        return hash(self.payload)

    def __eq__(self, other):
        return hash(self) == hash(other)
