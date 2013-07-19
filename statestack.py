import libtcodpy as libtcod
import frame
import gamestate


class StateStack(object):
    def __init__(self):
        self._stack = []
        self._current_game_state_cache = None

    def main_loop(self):
        while len(self._stack) > 0:
            state = self.peek()
            state.update()
            state.draw()
            libtcod.console_flush()
            frame.current_frame += 1

    def push(self, state):
        state.current_stack = self
        self._stack.append(state)
        if isinstance(state, gamestate.GameStateBase):
            self._current_game_state_cache = state

    def peek(self):
        return self._stack[-1]

    def get_game_state(self):
        return self._current_game_state_cache

    def pop(self):
        state = self._stack.pop()
        state.current_stack = None
        if (state is self._current_game_state_cache):
            self._current_game_state_cache is None
        return state
