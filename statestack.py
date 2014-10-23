import frame
import gui
import rectfactory
import colors


class StateStack(object):
    def __init__(self):
        self._stack = []

    def main_loop(self):
        while len(self._stack) > 0:
            frame.current_frame += 1
            state = self.peek()
            state.update()
            if not state is self.peek():
                continue
            state.draw()

    def push(self, state):
        state.current_stack = self
        self._stack.append(state)

    def peek(self):
        if len(self._stack) < 1:
            return None
        return self._stack[-1]

    def pop(self):
        state = self._stack.pop()
        state.current_stack = None
        return state

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

    def pop_to_game_state(self):
        if not self._game_state:
            raise Exception("Cannot pop to GameState without GameState set.")
        while len(self._stack) > 0 and not self.peek() is self._game_state:
            self.pop()

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
