import constants


class Camera(object):
    def __init__(self, screen_position, camera_offset):
        self.screen_position = screen_position
        self.camera_offset = camera_offset

    @property
    def screen_center_position(self):
        result = self.camera_offset + (constants.GAME_STATE_WIDTH / 2,
                                       constants.GAME_STATE_HEIGHT / 2)
        return result

    @property
    def offset(self):
        return self.screen_position + self.camera_offset

    def dungeon_to_screen_position(self, position):
        return position - self.camera_offset + self.screen_position

    def update(self, player):
        delta = player.position - self.screen_center_position
        self.camera_offset = self.camera_offset + delta
