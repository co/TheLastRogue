class Camera(object):
    def __init__(self, screen_position, camera_offset):
        self._screen_position = screen_position
        self.camera_offset = camera_offset

    @property
    def offset(self):
        return self._screen_position + self.camera_offset
