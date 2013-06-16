class Tile(object):
    def __init__(self, terrain):
        self.terrain = terrain
        self.entity = None
        self.items = []
        self.sceneries = []

    def draw(self, position, is_seen):
        self.terrain.draw(position, is_seen)
        for scenery in self.sceneries:
            scenery.draw(position, is_seen)
        for item in self.items:
            item.draw(position, is_seen)
        if(not self.entity is None):
            self.entity.draw(is_seen)
