import counter
import gametime
import colors
import entity
import player
import rng
import messenger
import libtcodpy as libtcod


class Monster(entity.Entity):
    def __init__(self, game_state):
        super(Monster, self).__init__(game_state)

    def kill_and_remove(self):
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
        if(not found_player is None and
           not found_player.has_status(entity.StatusFlags.INVISIBILE)):
            return found_player
        return None

    def set_path_to_player_if_seen(self):
        player = self.get_player_if_seen()
        if(player is None):
            return False
        mx, my = self.position
        px, py = player.position
        print "path set to player pos", px, py
        libtcod.path_compute(self.path, mx, my, px, py)
        return True

    def step_looking_for_player(self):
        self.set_path_to_player_if_seen()
        if(not self.has_path()):
            print "time to walk randomly"
            self.set_path_to_random_walkable_point()
        step_succeeded = self.try_step_path()
        return step_succeeded


class RatMan(Monster):
    def __init__(self, game_state):
        super(RatMan, self).__init__(game_state)
        self.hp = counter.Counter(10, 10)
        self._name = "Rat-Man"
        self.death_message = "The Rat-Man is beaten to a pulp."
        self._color_fg = colors.DB_TAHITI_GOLD
        self._symbol = 'r'

    def act(self):
        self.step_looking_for_player()
        if(rng.coin_flip() and self.can_see_player()):
            message = "The rat-man looks at you."
            messenger.messenger.message(message)
        return gametime.single_turn


class Jerico(RatMan):
    def __init__(self, game_state):
        super(Jerico, self).__init__(game_state)
        self._name = "Jerico"
        self.death_message = "Jerico the quick is no more."
        self._color_fg = colors.DB_GOLDEN_FIZZ
        self.energy_recovery = gametime.double_energy_gain


class Slime(Monster):
    """
    Slime monsters, can swallow the player.
    They fight by entering the tile of another entity.
    """
    def __init__(self, game_state):
        super(Slime, self).__init__(game_state)
        self._name = "Slime"
        self.death_message = "The slime melts away."
        self._color_fg = colors.DB_ATLANTIS
        self._symbol = libtcod.CHAR_DIAMOND

        self.hp = counter.Counter(20, 20)
        self.energy_recovery = gametime.half_energy_gain

    def _can_fit_on_tile(self, tile):
        """
        Slime monsters fight by entering the tile of another entity.
        Therefore it must override '_can_fit_on_tile' so it doesn't think
        A tile with an entity is too crowded.
        """
        entities_on_tile = tile.game_pieces[self.piece_type]
        if(len(entities_on_tile) == 0):
            return True
        elif(len(entities_on_tile) > 1):
            return False
        else:
            return (not isinstance(entities_on_tile[0], Slime))

    def act(self):
        """
        Slime monsters pursues the player.
        """
        player = self.get_player_if_seen()
        if(not player is None and (player.position == self.position)):
            pass  # eat player.
        else:
            self.step_looking_for_player()

        if(rng.coin_flip() and self.can_see_player()):
            message = "The slime seems to wobble with happiness."
            messenger.messenger.message(message)
        return gametime.single_turn

    def try_hit(self, position):
        """
        Slime monsters never "hit" anything, they move into something.
        """
        return False


class StoneStatue(Monster):
    def __init__(self, game_state):
        super(StoneStatue, self).__init__(game_state)
        self.hp = counter.Counter(30, 30)
        self._name = "stone statue"
        self.death_message = "The stone statue shatters pieces, "\
            "sharp rocks covers the ground."
        self._color_fg = colors.DB_TOPAZ
        self._symbol = '&'

    def act(self):
        if(rng.coin_flip() and self.can_see_player()):
            message = "The stone statue casts a long shadow on the floor."
            messenger.messenger.message(message)
        return gametime.single_turn
