import constants
import geometry as geo
import settings


class Camera(object):
    def __init__(self, screen_position, camera_offset):
        self.screen_position = screen_position
        self.camera_offset = camera_offset

    @property
    def screen_center_position(self):
        result = geo.add_2d(self.camera_offset,
                            (settings.WINDOW_WIDTH / 2,
                             settings.WINDOW_HEIGHT / 2))
        return result

    @property
    def offset(self):
        return geo.add_2d(self.screen_position, self.camera_offset)

    def dungeon_to_screen_position(self, position):
        return geo.add_2d(geo.sub_2d(position, self.camera_offset),
                          self.screen_position)

    def update(self, player):
        position = player.position.value
        delta = geo.sub_2d(position, self.screen_center_position)
        self.camera_offset = geo.add_2d(self.camera_offset, delta)
