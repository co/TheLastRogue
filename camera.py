import colors
from console import console
import constants
import geometry as geo
import settings


class Camera(object):
    def __init__(self, screen_position, camera_offset, game_state):
        self.screen_position = screen_position
        self._camera_offset = camera_offset
        x_frame = max(int(settings.SCREEN_WIDTH * 0.2),
                      constants.LEFT_SIDE_BAR_WIDTH + constants.COMMON_SIGHT_RADIUS + 2)
        y_frame = int(settings.SCREEN_WIDTH * 0.3)
        y_bottom_frame = settings.SCREEN_HEIGHT - max(y_frame, constants.GUI_BOX_HEIGHT +
                                                               constants.COMMON_SIGHT_RADIUS + 2)
        self.x_graze_edge = [x_frame, settings.SCREEN_WIDTH - x_frame]
        self.y_graze_edge = [y_frame, y_bottom_frame]
        self.game_state = game_state

    @property
    def screen_center_position(self):
        result = geo.add_2d(self.camera_offset,
                            (settings.SCREEN_WIDTH / 2,
                             settings.SCREEN_HEIGHT / 2))
        return result

    @property
    def offset(self):
        return geo.add_2d(self.screen_position, self.camera_offset)

    @property
    def camera_offset(self):
        return self._camera_offset

    @camera_offset.setter
    def camera_offset(self, value):
        if not value == self._camera_offset:
            self._camera_offset = value

    def dungeon_to_screen_position(self, position):
        return geo.add_2d(geo.sub_2d(position, self.camera_offset),
                          self.screen_position)

    def screen_to_dungeon_position(self, position):
        return geo.sub_2d(geo.add_2d(position, self.camera_offset),
                          self.screen_position)

    def scroll_graze_delta(self, position):
        x_delta = 0
        y_delta = 0
        x_delta += max(0, self.x_graze_edge[0] - position[0])
        x_delta -= max(0, position[0] - self.x_graze_edge[1])
        y_delta += max(0, self.y_graze_edge[0] - position[1])
        y_delta -= max(0, position[1] - self.y_graze_edge[1])
        return - x_delta, - y_delta

    def update(self, player):
        position = player.position.value
        delta = self.scroll_graze_delta(self.dungeon_to_screen_position(position))
        self.camera_offset = geo.add_2d(self.camera_offset, delta)

    def center_on_entity(self, entity):
        position = entity.position.value
        delta = geo.sub_2d(position, self.screen_center_position)
        self.camera_offset = geo.add_2d(self.camera_offset, delta)

    def draw_graze_rect(self):
        for x in range(self.x_graze_edge[0], self.x_graze_edge[1]):
            console.set_color_bg((x, self.y_graze_edge[0]), colors.YELLOW)
            console.set_color_bg((x, self.y_graze_edge[1]), colors.YELLOW)
        for y in range(self.y_graze_edge[0], self.y_graze_edge[1]):
            console.set_color_bg((self.x_graze_edge[0], y), colors.YELLOW)
            console.set_color_bg((self.x_graze_edge[1], y), colors.YELLOW)

