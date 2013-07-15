import libtcodpy as libtcod
import frame
import gamestate


class StateStack(object):
    def __init__(self):
        self._stack = []

    def main_loop(self):
        while len(self._stack) > 0:
            state = self.peek()
            state.update()
            state.draw()
            libtcod.console_flush()
            frame.current_frame += 1

    def push(self, game_state):
        game_state.current_stack = self
        self._stack.append(game_state)

    def peek(self):
        return self._stack[-1]

    def get_game_state(self):
        return next(state for state in self._stack
                    if isinstance(state, gamestate.GameStateBase))

    def pop(self):
        state = self._stack.pop()
        state.current_stack = None
        return state
