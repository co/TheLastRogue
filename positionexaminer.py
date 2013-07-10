import gamestate
import vector2d
import frame
import constants
import libtcodpy as libtcod
import colors
import inputhandler
import numpy


class PositionExaminer(gamestate.GameState):
    def __init__(self, position, camera, background_state=None,
                 max_distance=numpy.inf):
        self.cursor_position = position
        self.max_distance = max_distance
        self.camera = camera
        self.cursor_symbol = 'X'
        self.cursor_color = colors.CURSOR
        self._background_state = background_state

    def update(self):
        key = inputhandler.get_keypress()
        self._handle_directional_input(key)
        self._handle_escape(key)

    def _handle_directional_input(self, key):
        step_size = 1
        if inputhandler.is_special_key_pressed(inputhandler.KEY_SHIFT):
            step_size = 5
        if key == inputhandler.UP:
            self.offset_cursor_position((0, -step_size))
        if key == inputhandler.DOWN:
            self.offset_cursor_position((0, step_size))
        if key == inputhandler.LEFT:
            self.offset_cursor_position((-step_size, 0))
        if key == inputhandler.RIGHT:
            self.offset_cursor_position((step_size, 0))

    def offset_cursor_position(self, offset):
        new_cursor_position = self.cursor_position + offset

        if(vector2d.chess_distance(new_cursor_position, self.start_position) >
           self.max_distance):
            return
        self.cursor_position = new_cursor_position

    def _handle_escape(self, key):
        if key == inputhandler.ESCAPE:
            gamestate.game_state_stack.pop()

    def _draw_background(self):
        if(not self._background_state is None):
            self._background_state.draw()

    def _draw_cursor(self):
        if((frame.current_frame % (constants.FPS / 10)) < constants.FPS / 40):
            return
        position = self.cursor_position + self.camera.offset
        x, y = position.x, position.y
        libtcod.console_set_char(0, x, y, self.cursor_symbol)
        libtcod.console_set_char_foreground(0, x, y, self.cursor_color)

    def draw(self):
        self._draw_background()
        self._draw_cursor()


class PositionSelector(PositionExaminer):
    def __init__(self, position, camera,
                 return_position, background_state=None,
                 max_distance=numpy.inf):
        super(PositionSelector, self).__init__(position, camera,
                                               background_state, max_distance)
        self._return_position = return_position

    def update(self):
        key = inputhandler.get_keypress()
        self._handle_directional_input(key)
        self._handle_escape(key)
        self._handle_enter(key)

    def _handle_enter(self, key):
        if key == inputhandler.ENTER:
            self._return_position = self.cursor_position
            gamestate.game_state_stack.pop()


class MissileDestinationSelector(PositionSelector):
    def __init__(self, position, camera, entity,
                 return_position, background_state=None,
                 max_distance=numpy.inf):
        super(MissileDestinationSelector,
              self).__init__(position, camera, return_position,
                             background_state, max_distance)
        self.start_position = position.copy()
        self.entity = entity

    def _draw_path(self):
        sx, sy = self.start_position.x, self.start_position.y
        dx, dy = self.cursor_position.x, self.cursor_position.y
        libtcod.line_init(sx, sy, dx, dy)
        x, y = libtcod.line_step()
        while (not x is None):
            self._draw_path_part(x, y)
            x, y = libtcod.line_step()

    def _draw_path_part(self, x, y):
        screen_x = x + self.camera.offset.x
        screen_y = y + self.camera.offset.y
        terrain = self.entity.dungeon_level.tile_matrix[y][x].get_terrain()
        if(self.entity.can_see_point(x, y) and terrain.is_solid()):
            libtcod.console_set_char(0, screen_x, screen_y, " ")
            libtcod.console_set_char_background(0, screen_x, screen_y,
                                                colors.BLOCKED_PATH)
        else:
            libtcod.console_set_char_background(0, screen_x, screen_y,
                                                colors.PATH,
                                                libtcod.BKGND_ADD)

    def draw(self):
        self._draw_background()
        self._draw_path()
        self._draw_cursor()
