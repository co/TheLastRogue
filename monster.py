import counter
import colors
import entity
import messenger


class Monster(entity.Entity):
    def __init__(self):
        super(Monster, self).__init__()
        self.fov_map = None


class RatMan(Monster):
    def __init__(self):
        super(RatMan, self).__init__()
        self.hp = counter.Counter(10, 10)
        self.name = "Rat-man"

    @staticmethod
    def get_symbol():
        return 'r'

    @staticmethod
    def get_color_fg():
        return colors.DB_TAHITI_GOLD

    def update(self, dungeon_level, player):
        self.step_random_direction(dungeon_level)
        message = "The rat-man looks at you."
        messenger.messenger.message(messenger.Message(message))
