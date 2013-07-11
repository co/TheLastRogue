import libtcodpy as libtcod
import frame


class GameStateStack(object):
    def __init__(self):
        self._stack = []

    def main_loop(self):
        while len(self._stack) > 0:
            state = self.peek()
            state.draw()
            libtcod.console_flush()
            state.update()
            frame.current_frame += 1

    def push(self, game_state):
        game_state.current_stack = self
        self._stack.append(game_state)

    def peek(self):
        return self._stack[-1]

    def pop(self):
        state = self._stack.pop()
        state.current_stack = None
        return state


class GameState(object):
    def __init__(self):
        self.current_stack = None
        pass

    def update(self):
        pass

    def draw(self):
        pass
