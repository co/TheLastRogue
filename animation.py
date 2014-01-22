from console import console
import settings


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
        self.player = game_state.player

    def run_animation(self):
        for point in self.path:
            if not self.player.dungeon_mask.can_see_point(point):
                continue
            self.game_state.prepare_draw()
            self.print_missile_at_point(point)
            for _ in range(settings.MISSILE_ANIMATION_DELAY):
                console.flush()

    def print_missile_at_point(self, point):
        x, y = self.camera.dungeon_to_screen_position(point)
        console.set_color_fg((x, y), self.color_fg)
        console.set_symbol((x, y), self.symbol)


def animate_flight(game_state, path, symbol_char, color_fg):
    flight_animation = MissileAnimation(game_state, symbol_char, color_fg, path)
    flight_animation.run_animation()