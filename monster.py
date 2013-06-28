import counter
import colors
import entity
import player
import rng
import messenger
import libtcodpy as libtcod


class Monster(entity.Entity):
    def __init__(self):
        super(Monster, self).__init__()

    def kill(self):
        self.hp.set_min()
        self.try_remove_from_dungeon()
        messenger.messenger.message(messenger.Message(self.death_message))

    def can_see_player(self):
        seen_entities = self.get_seen_entities()
        return any(isinstance(entity, player.Player)
                   for entity in seen_entities)

    def get_player_if_seen(self):
        seen_entities = self.get_seen_entities()
        found_player = next((entity for entity in seen_entities
                             if(isinstance(entity, player.Player))),
                            None)
        return found_player

    def set_path_to_player_if_seen(self):
        player = self.get_player_if_seen()
        if(player is None):
            return False
        libtcod.path_compute(self.path, self.position.x, self.position.y,
                             player.position.x, player.position.y)
        return True

    def step_looking_for_player(self):
        self.set_path_to_player_if_seen()
        step_succeeded = self.try_step_path()
        return step_succeeded


class RatMan(Monster):
    def __init__(self):
        super(RatMan, self).__init__()
        self.hp = counter.Counter(10, 10)
        self.name = "Rat-Man"
        self.death_message = "The Rat-Man is beaten to a pulp."

    @staticmethod
    def get_symbol():
        return 'r'

    @staticmethod
    def get_color_fg():
        return colors.DB_TAHITI_GOLD

    def update(self, player):
        self.step_looking_for_player()
        if(rng.coin_flip() and self.can_see_player()):
            message = "The rat-man looks at you."
            messenger.messenger.message(messenger.Message(message))


class StoneStatue(Monster):
    def __init__(self):
        super(StoneStatue, self).__init__()
        self.hp = counter.Counter(30, 30)
        self.name = "stone statue"
        self.death_message = "The stone statue shatters pieces, "\
            "sharp rocks covers the ground."

    @staticmethod
    def get_symbol():
        return '&'

    @staticmethod
    def get_color_fg():
        return colors.DB_TOPAZ

    def update(self, player):
        if(rng.coin_flip() and self.can_see_player()):
            message = "The stone statue casts a long shadow on the floor."
            messenger.messenger.message(messenger.Message(message))
