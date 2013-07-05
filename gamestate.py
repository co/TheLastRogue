import libtcodpy as libtcod


class GameStateStack(object):
    def __init__(self):
        self._stack = []

    def main_loop(self):
        while len(self._stack) > 0:
            state = self.peek()
            state.draw()
            libtcod.console_flush()
            state.update()

    def push(self, game_state):
        self._stack.append(game_state)

    def peek(self):
        return self._stack[-1]

    def pop(self):
        return self._stack.pop()


class GameState(object):
    def __init__(self):
        pass

    def update(self):
        pass

    def draw(self):
        pass

game_state_stack = GameStateStack()
