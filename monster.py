from monsteractor import ChasePlayerActor
from actor import DoNothingActor
from attacker import Attacker
from position import Position
from damage import DamageTypes, Damage
import equipment
from dungeonlevelcomposite import DungeonLevel
from statusflags import StatusFlags
from compositecore import Composite, Leaf
from sightradius import SightRadius
from dungeonmask import DungeonMask
from gamepiecetype import GamePieceType
from memorymap import MemoryMap
from composite import Description, GraphicChar, MovementSpeed, Vision
from composite import Health, Strength, AttackSpeed, Faction, Inventory
from composite import CharPrinter, GameState, EntityMessages, Path
from entityeffect import EffectQueue
from mover import EntityMover, CanShareTileEntityMover
from action import PickUpItemAction
from ondeathaction import EntityDeathAction
import gametime
import symbol
import colors

import rng
import messenger


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


class Slime(Composite):
    """
    A composite component representing a Ratman monster.
    """
    def __init__(self, game_state):
        super(Slime, self).__init__()
        self.add_child(GamePieceType(GamePieceType.ENTITY))

        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(CanShareTileEntityMover())

        self.add_child(EntityMessages(("The slime seems to",
                                       "wobble with happiness."),
                                      ("The slime melts away.")))
        self.add_child(Description("Slime",
                                   ("Slime, slime, slime. Ugh, I hate Slimes."
                                    "It seems to be looking at you...")))
        self.add_child(GraphicChar(None, colors.GREEN,
                                   symbol.SLIME))
        self.add_child(CharPrinter())
        self.add_child(EntityDeathAction())

        self.add_child(Faction(Faction.MONSTER))
        self.add_child(Health(20))
        self.add_child(Strength(6))
        self.add_child(MovementSpeed(gametime.double_turn))
        self.add_child(AttackSpeed(gametime.single_turn))
        self.add_child(StatusFlags())

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

        self.add_child(EntityShareTileEffect
                       (DissolveEntitySlimeShareTileEffect()))


class EntityShareTileEffect(Leaf):
    """
    Defines an effect that sharing tile with this parent entity will result in.
    """
    def __init__(self, effect):
        super(EntityShareTileEffect, self).__init__()
        self.component_type = "entity_share_tile_effect"
        self.effect = effect

    def share_tile_effect_tick(self, sharing_entity, time_spent):
        if(not sharing_entity is self.parent):
            self.effect(source_entity=self.parent,
                        target_entity=sharing_entity,
                        time=time_spent)


class DissolveEntitySlimeShareTileEffect(object):
    def __init__(self):
        pass

    def __call__(self, **kwargs):
        target_entity = kwargs["target_entity"]
        source_entity = kwargs["source_entity"]
        time = kwargs["time"]
        strength = source_entity.strength.value
        damager = Damage(strength, strength / 3,
                         [DamageTypes.ACID, DamageTypes.PHYSICAL],
                         time / gametime.single_turn)
        damager.damage_entity(source_entity, target_entity)


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
