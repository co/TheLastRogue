from monsteractor import ChasePlayerActor
from actor import DoNothingActor
from attacker import Attacker
from position import Position
import equipment
from dungeonlevelcomposite import DungeonLevel
from statusflags import StatusFlags
from compositecore import Composite
from sightradius import SightRadius
from dungeonmask import DungeonMask
from gamepiecetype import GamePieceType
from memorymap import MemoryMap
from composite import Description, GraphicChar, MovementSpeed, Vision
from composite import Health, Strength, AttackSpeed, Faction, Inventory
from composite import CharPrinter, GameState, EntityMessages, Path
from entityeffect import EffectQueue
from mover import EntityMover
from action import PickUpItemAction
from ondeathaction import EntityDeathAction
import gametime
import symbol
import colors

import rng
import messenger


#
#class Monster(entity.Entity):
#    def __init__(self, game_state):
#        super(Monster, self).__init__(game_state)
#
#    def kill_and_remove(self):
#        self.hp.set_min()
#        self.on_death()
#        if(self.has_status(entity.StatusFlags.LEAVES_CORPSE)):
#            spawner.spawn_corpse_of_entity(self)
#        self.try_remove_from_dungeon()
#        messenger.messenger.message(messenger.Message(self.death_message))
#
#    def can_see_player(self):
#        seen_entities = self.get_seen_entities()
#        return any(isinstance(entity, player.Player)
#                   for entity in seen_entities)
#
#    def get_player_if_seen(self):
#        seen_entities = self.get_seen_entities()
#        found_player = next((entity for entity in seen_entities
#                             if(isinstance(entity, player.Player))),
#                            None)
#        if(not found_player is None and
#           not found_player.has_status(entity.StatusFlags.INVISIBILE)):
#            return found_player
#        return None
#
#    def set_path_to_player_if_seen(self):
#        player = self.get_player_if_seen()
#        if(player is None):
#            return False
#        mx, my = self.position
#        px, py = player.position
#        libtcod.path_compute(self.path, mx, my, px, py)
#        return True
#
#    def step_looking_for_player(self):
#        self.set_path_to_player_if_seen()
#        if(not self.has_path()):
#            self.set_path_to_random_walkable_point()
#        step_succeeded = self.try_step_path()
#        return step_succeeded
#

class Ratman(Composite):
    """
    A composite component representing a Ratman monster.
    """
    def __init__(self, game_state):
        super(Ratman, self).__init__()
        self.add_child(GamePieceType(GamePieceType.ENTITY))

        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(EntityMover())

        self.add_child(EntityMessages("The ratman looks at you.",
                                      "The ratman is beaten to a pulp."))
        self.add_child(Description("Ratman",
                                   "A Rat/Man hybrid it looks hostile."))
        self.add_child(GraphicChar(None, colors.ORANGE,
                                   symbol.RATMAN))
        self.add_child(CharPrinter())
        self.add_child(EntityDeathAction())

        self.add_child(Faction(Faction.MONSTER))
        self.add_child(Health(10))
        self.add_child(Strength(2))
        self.add_child(MovementSpeed(gametime.single_turn))
        self.add_child(AttackSpeed(gametime.single_turn))
        self.add_child(StatusFlags([StatusFlags.LEAVES_CORPSE,
                                    StatusFlags.CAN_OPEN_DOORS]))

        self.add_child(SightRadius(6))
        self.add_child(DungeonMask())
        self.add_child(Vision())

        self.add_child(MemoryMap())
        self.add_child(Inventory())
        self.add_child(Path())
        self.add_child(ChasePlayerActor())
        self.add_child(GameState(game_state))
        self.add_child(equipment.Equipment())
        self.add_child(EffectQueue())
        self.add_child(PickUpItemAction())
        self.add_child(Attacker())

    def act(self):
        self.step_looking_for_player()
        if(rng.coin_flip() and self.can_see_player()):
            message = "The rat-man looks at you."
            messenger.messenger.message(message)
        return gametime.single_turn


class Jerico(Ratman):
    def __init__(self, game_state):
        super(Jerico, self).__init__(game_state)
        self._name = "Jerico"
        self.death_message = "Jerico the quick is no more."
        self.gfx_char.color_fg = colors.YELLOW
        self.energy_recovery = gametime.double_energy_gain


class StoneStatue(Composite):
    """
    A composite component representing a Ratman monster.
    """
    def __init__(self, game_state):
        super(StoneStatue, self).__init__()
        self.add_child(GamePieceType(GamePieceType.ENTITY))

        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(EntityMover())

        self.add_child(EntityMessages(("The stone statue casts a"
                                       "long shadow on the floor."),
                                      ("The stone statue shatters pieces, "
                                       "sharp rocks covers the ground.")))
        self.add_child(Description("Stone Statue",
                                   ("A Statue made out of stone stands tall."
                                    "It seems to be looking at you...")))
        self.add_child(GraphicChar(None, colors.GRAY,
                                   symbol.GOLEM))
        self.add_child(CharPrinter())
        self.add_child(EntityDeathAction())

        self.add_child(Faction(Faction.MONSTER))
        self.add_child(Health(30))
        self.add_child(Strength(0))
        self.add_child(MovementSpeed(gametime.single_turn))
        self.add_child(AttackSpeed(gametime.single_turn))
        self.add_child(StatusFlags([StatusFlags.LEAVES_CORPSE,
                                    StatusFlags.CAN_OPEN_DOORS]))

        self.add_child(SightRadius(6))
        self.add_child(DungeonMask())
        self.add_child(Vision())

        self.add_child(MemoryMap())
        self.add_child(Inventory())
        self.add_child(Path())
        self.add_child(DoNothingActor())
        self.add_child(GameState(game_state))
        self.add_child(equipment.Equipment())
        self.add_child(EffectQueue())
        self.add_child(PickUpItemAction())
        self.add_child(Attacker())

#        self.hp = counter.Counter(30, 30)
#        self._name = "stone statue"
#        self.death_message = "The stone statue shatters pieces, "\
#            "sharp rocks covers the ground."
#        self.gfx_char.color_fg = colors.GRAY
#        self._permanent_status_flags = set()
#        self.gfx_char.symbol = symbol.GOLEM

#class Slime(Monster):
#    """
#    Slime monsters, can swallow the player.
#    They fight by entering the tile of another entity.
#    """
#    def __init__(self, game_state):
#        super(Slime, self).__init__(game_state)
#        self._name = "Slime"
#        self.death_message = "The slime melts away."
#        self.gfx_char.color_fg = colors.GREEN
#        self.gfx_char.symbol = symbol.SLIME
#        # The slime cannot open doors and does not leave a corpse.
#        self._permanent_status_flags = set()
#
#        self.hp = counter.Counter(20, 20)
#        self.energy_recovery = gametime.half_energy_gain
#
#    def _can_fit_on_tile(self, tile):
#        """
#        Slime monsters fight by entering the tile of another entity.
#        Therefore it must override '_can_fit_on_tile' so it doesn't think
#        A tile with an entity is too crowded.
#        """
#        entities_on_tile = tile.game_pieces[self.piece_type]
#        if(len(entities_on_tile) == 0):
#            return True
#        elif(len(entities_on_tile) > 1):
#            return False
#        else:
#            return (not isinstance(entities_on_tile[0], Slime))
#
#    def act(self):
#        """
#        Slime monsters pursues the player.
#        Slime monsters may stay at the same tile as other entities
#        and will hurt them in the process.
#        """
#        player = self.get_player_if_seen()
#        if(not player is None and (player.position == self.position)):
#            pass  # eat player.
#        else:
#            self.step_looking_for_player()
#
#        if(not player is None and (player.position == self.position)):
#            slime_status = entity.StatusFlags.SWALLOWED_BY_SLIME
#            slime_status_adder = entityeffect.StatusAdder(self, player,
#                                                          slime_status, 2)
#            player.add_entity_effect(slime_status_adder)
#            self.hit(player)
#
#        if(rng.coin_flip() and self.can_see_player()):
#            message = "The slime seems to wobble with happiness."
#            messenger.messenger.message(message)
#
#        return gametime.single_turn
#
#    def try_hit(self, position):
#        """
#        Slime monsters never "hit" anything, they move into something.
#        """
#        return False
#
#
#class StoneStatue(Monster):
#    def __init__(self, game_state):
#        super(StoneStatue, self).__init__(game_state)
#        self.hp = counter.Counter(30, 30)
#        self._name = "stone statue"
#        self.death_message = "The stone statue shatters pieces, "\
#            "sharp rocks covers the ground."
#        self.gfx_char.color_fg = colors.GRAY
#        self._permanent_status_flags = set()
#        self.gfx_char.symbol = symbol.GOLEM
#
#    def act(self):
#        if(rng.coin_flip() and self.can_see_player()):
#            message = "The stone statue casts a long shadow on the floor."
#            messenger.messenger.message(message)
#        return gametime.single_turn
