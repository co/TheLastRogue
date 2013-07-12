import libtcodpy as libtcod


class InstantAnimation(object):
    def __init__(self, game_state):
        self.game_state = game_state

    def run_animation(self):
        pass


class MissileAnimation(InstantAnimation):
    def __init__(self, game_state, symbol, color_fg, path):
        super(MissileAnimation, self).__init__(game_state)
        self.symbol = symbol
        self.color_fg = color_fg
        self.path = path
        self.camera = game_state.current_stack.get_game_state().camera

    def run_animation(self):
        for point in self.path:
            self.game_state.draw()
            self.print_missile_at_point(point)
            libtcod.console_flush()

    def print_missile_at_point(self, point):
        p = self.camera.dungeon_to_screen_position(point)
        x, y = p.x, p.y
        libtcod.console_set_char_foreground(0, x, y, self.color_fg)
        libtcod.console_set_char(0, x, y, self.symbol)
