import geometry as geo
from console import console
import libtcodpy as libtcod
import colors
import inputhandler
import numpy
import state


class PositionExaminer(state.State):
    def __init__(self, state_stack, position, background_state,
                 max_distance=numpy.inf):
        super(PositionExaminer, self).__init__()
        self._state_stack = state_stack
        self.cursor_position = position
        self.max_distance = max_distance
        self.camera = background_state.current_stack.get_game_state().camera
        self.cursor_symbol = 'X'
        self.cursor_color = colors.CURSOR
        self._background_state = background_state

    def update(self):
        key = inputhandler.handler.get_keypress()
        self._handle_directional_input(key)
        self._handle_escape(key)
        self._handle_enter(key)

    def _handle_directional_input(self, key):
        step_size = 1
        if inputhandler.handler.is_special_key_pressed(inputhandler.KEY_SHIFT):
            step_size = 5
        if key in inputhandler.move_controls:
            dx, dy = inputhandler.move_controls[key]
            self.offset_cursor_position((dx * step_size, dy * step_size))

    def offset_cursor_position(self, offset):
        new_cursor_position = geo.add_2d(self.cursor_position, offset)

        if(geo.chess_distance(new_cursor_position, self.start_position) >
           self.max_distance):
            return
        self.cursor_position = new_cursor_position

    def _handle_escape(self, key):
        if key == inputhandler.ESCAPE:
            self._exit()

    def _handle_enter(self, key):
        if key == inputhandler.ENTER:
            self._exit()

    def _draw_background(self):
        if(not self._background_state is None):
            self._background_state.prepare_draw()

    def _draw_cursor(self):
        position = self.camera.dungeon_to_screen_position(self.cursor_position)
        console.set_symbol(position, self.cursor_symbol)
        console.set_color_fg(position, self.cursor_color)

    def _exit(self):
        self._draw_background()
        self._state_stack.pop()

    def draw(self):
        self._draw_background()
        self._draw_cursor()
        libtcod.console_flush()


class PositionSelector(PositionExaminer):
    def __init__(self, state_stack, position, background_state,
                 max_distance=numpy.inf):
        super(PositionSelector, self).__init__(state_stack, position,
                                               background_state, max_distance)
        self._return_position = None

    @property
    def selected_position(self):
        return self._return_position

    def _handle_enter(self, key):
        if key == inputhandler.ENTER:
            self._return_position = self.cursor_position
            self._exit()


class MissileDestinationSelector(PositionSelector):
    def __init__(self, state_stack, position, entity, background_state,
                 max_distance=numpy.inf, init_target=None):
        super(MissileDestinationSelector,
              self).__init__(state_stack, position,
                             background_state, max_distance)
        self.start_position = position
        self.entity = entity
        self.selected_path = None
        if not init_target is None:
            self.cursor_position = init_target

    def _get_current_path(self):
        result = []
        sx, sy = self.start_position
        dx, dy = self.cursor_position
        libtcod.line_init(sx, sy, dx, dy)
        x, y = libtcod.line_step()
        while (not x is None):
            result.append((x, y))
            x, y = libtcod.line_step()
        result.append(self.cursor_position)
        return result

    def _draw_path(self):
        path = self._get_current_path()
        for point in path:
            self._draw_path_point(point)

    def _handle_escape(self, key):
        if key == inputhandler.ESCAPE:
            self.selected_path = None
            self._exit()

    def _handle_enter(self, key):
        if key == inputhandler.ENTER:
            self.selected_path = self._get_current_path()
            self._exit()

    def _draw_path_point(self, point):
        screen_position = self.camera.dungeon_to_screen_position(point)
        terrain = self.entity.dungeon_level.\
            get_tile_or_unknown(point).get_terrain()
        if(self.entity.can_see_point(point) and terrain.is_solid()):
            console.set_symbol(screen_position, ' ')
            console.set_color_bg(screen_position, colors.BLOCKED_PATH)
        else:
            console.set_color_bg(screen_position, colors.PATH,
                                 libtcod.BKGND_ADD)

    def draw(self):
        self._draw_background()
        self._draw_path()
        self._draw_cursor()
        libtcod.console_flush()
