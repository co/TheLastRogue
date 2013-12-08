import gamestate
import frame
import gui
import rectfactory
import colors


class StateStack(object):
    def __init__(self):
        self._stack = []
        self._current_game_state_cache = None

    def main_loop(self):
        while len(self._stack) > 0:
            state = self.peek()
            state.update()
            state.draw()
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
        if state is self._current_game_state_cache:
            self._current_game_state_cache is None
        return state

    def pop_to_game_state(self):
        while(len(self._stack) > 0 and
              not isinstance(self.peek(), gamestate.GameStateBase)):
            self.pop()

    def pop_to_main_menu(self):
        while len(self._stack) > 1:
            self.pop()


class GameMenuStateStack(StateStack):
    def __init__(self, game_state):
        super(GameMenuStateStack, self).__init__()
        self._grayout_rectangle = gui.RectangleChangeColor(rectfactory.full_screen_rect(), colors.BLACK)
        self._stack = []
        self._game_state = game_state

    def main_loop(self):
        while len(self._stack) > 0:
            state = self.peek()
            self._draw_background()
            state.draw()
            state.update()
        self._game_state.force_draw()

    def get_game_state(self):
        return self._game_state

    def push(self, state):
        state.current_stack = self
        self._draw_background()
        self._stack.append(state)

    def pop(self):
        state = self._stack.pop()
        self._draw_background()
        state.current_stack = None
        return state

    def _draw_background(self):
        self._game_state.prepare_draw()
        self._grayout_rectangle.draw()

    def peek(self):
        return self._stack[-1]
