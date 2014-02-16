from console import console
from graphic import GraphicChar
import icon
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


def animate_point(game_state, position, graphic_chars):
    if not game_state.player.dungeon_mask.can_see_point(position):
        return
    camera = game_state.current_stack.get_game_state().camera
    x, y = camera.dungeon_to_screen_position(position)
    for graphic_char in graphic_chars:
        game_state.prepare_draw()
        console.set_color_fg((x, y), graphic_char.color_fg)
        console.set_symbol((x, y), graphic_char.icon)
        for _ in range(settings.MISSILE_ANIMATION_DELAY):
            console.flush()


def animate_fall(target_entity):
    color_fg = target_entity.graphic_char.color_fg
    target_entity.game_state.value.force_draw()
    graphic_chars = [target_entity.graphic_char,
                     GraphicChar(None, color_fg, icon.BIG_CENTER_DOT),
                     GraphicChar(None, color_fg, "*"),
                     GraphicChar(None, color_fg, "+"),
                     GraphicChar(None, color_fg, icon.CENTER_DOT)]
    animate_point(target_entity.game_state.value, target_entity.position.value, graphic_chars)