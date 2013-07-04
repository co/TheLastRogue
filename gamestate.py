class GameState(object):
    def __init__(self):
        pass

    def update(self):
        pass

    def draw(self):
        pass


class GameStateStack(object):
    def __init__(self):
        self._stack = []

    def update(self):
        while len(self._stack) > 0:
            state = self.peek
            state.update()

    def draw(self):
        while len(self._stack) > 0:
            state = self.peek
            state.draw()

    def push(self, game_state):
        self._stack.push(game_state)

    def peek(self):
        self._stack.peek()

    def pop(self):
        return self._stack.pop()
