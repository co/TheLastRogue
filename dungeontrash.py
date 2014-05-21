import random
from actor import DoNothingActor
from compositecore import Composite, Leaf
import gametime
from graphic import GraphicChar, CharPrinter
import icon
from mover import Mover
from position import Position, DungeonLevel
from stats import GamePieceTypes, DataTypes, DataPoint
from terrain import FallRemoveNonPlayerNonFlying
from text import Description
import colors


def set_corpse_components(corpse, game_state):
    corpse.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.DUNGEON_TRASH))
    corpse.set_child(Position())
    corpse.set_child(DungeonLevel())
    corpse.set_child(Description("A rotting corpse.",
                                 "A rotting corpse."))
    corpse.set_child(GraphicChar(None, colors.WHITE,
                               icon.CORPSE))
    corpse.set_child(FallRemoveNonPlayerNonFlying())
    corpse.set_child(CharPrinter())
    corpse.set_child(DoNothingActor())
    corpse.set_child(Mover())
    corpse.set_child(DataPoint(DataTypes.GAME_STATE, game_state))


class Corpse(Composite):
    """
    A corpse. Totally useless but looks nice
    and gives the user feedback when a monster dies.
    """
    def __init__(self, game_state):
        super(Corpse, self).__init__()
        set_corpse_components(self, game_state)


class ReplaceWithEntityAfterTime(Leaf):
    def __init__(self, time_out, entity_factory):
        super(ReplaceWithEntityAfterTime, self).__init__()
        self.component_type = "turn_into_entity_after_time"
        self.time_out = time_out
        self.entity_factory = entity_factory

    def on_tick(self, time):
        self.time_out -= time
        if self.time_out <= 0:
            entity = self.entity_factory(self.parent.game_state)
            position = self.parent.position.value
            dungeon_level = self.parent.dungeon_level.value
            entity.mover.try_move_roll_over(position, dungeon_level)
            self.parent.mover.try_remove_from_dungeon()


class CorpseTurnIntoEntity(Composite):
    """
    A corpse. Totally useless but looks nice
    and gives the user feedback when a monster dies.
    """
    def __init__(self, game_state, entity_factory):
        super(CorpseTurnIntoEntity, self).__init__()
        set_corpse_components(self, game_state)
        self.component_type = "turn_into_entity"
        self.set_child(ReplaceWithEntityAfterTime(random.randrange(7, 30) * gametime.single_turn, entity_factory))


class PoolOfBlood(Composite):
    """
    A pool of blood. Totally useless but looks nice
    and gives the user feedback when a monster is hurt.
    """
    def __init__(self):
        super(PoolOfBlood, self).__init__()
        self.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.DUNGEON_TRASH))
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(Description("A pool of blood.", "A pool of blood."))
        self.set_child(GraphicChar(None, colors.RED, random.choice(icon.BLOOD_ICONS)))
        self.set_child(CharPrinter())
        self.set_child(Mover())
