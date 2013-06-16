import Counter as counter
import Colors as colors
import Entity as entity


class Monster(entity.Entity):
    def __init__(self, position):
        super(Monster, self).__init__(position)
        self.fov_map = None

    def update(self, dungeon_level, player):
        pass


class RatMan(Monster):
    def __init__(self, position):
        super(RatMan, self).__init__(position)
        self.hp = counter.Counter(10, 10)

    @staticmethod
    def get_symbol():
        return 'r'

    @staticmethod
    def get_color_fg():
        return colors.DB_OILED_CEDAR

    def update(self, dungeon_level, player):
        self.step_random_direction(dungeon_level)
