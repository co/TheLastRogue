from compositecore import Composite, Leaf
from graphic import GraphicChar, CharPrinter
from mover import Mover
from position import Position, DungeonLevel
from stats import GamePieceType
from text import Description
import action
import colors
import symbol


class StairsDown(Composite):
    """
    Stairs Down allows the player to descend to the next level.
    """
    def __init__(self):
        super(StairsDown, self).__init__()
        self.add_child(GamePieceType(GamePieceType.DUNGEON_FEATURE))
        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(Description("Stairs Down",
                                   ("A dark pass way downward.",
                                    "Oh, what horrors awaits there?")))
        self.add_child(GraphicChar(None, colors.WHITE,
                                   symbol.STAIRS_DOWN))

        self.add_child(CharPrinter())
        self.add_child(DescendStairsAction())
        self.add_child(Mover())
        self.add_child(IsDungeonFeature())


class StairsUp(Composite):
    """
    Stairs up allows the player to ascend to the next level.
    """
    def __init__(self):
        super(StairsUp, self).__init__()
        self.add_child(GamePieceType(GamePieceType.DUNGEON_FEATURE))
        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(Description("Stairs Up",
                                   ("A way back, when the ",
                                    "nightmare becomes too real.")))
        self.add_child(GraphicChar(None, colors.WHITE,
                                   symbol.STAIRS_UP))
        self.add_child(CharPrinter())
        self.add_child(Mover())
        self.add_child(IsDungeonFeature())


class Fountain(Composite):
    """
    Drinking from the fountain makes the player stronger.
    """
    def __init__(self):
        super(Fountain, self).__init__()
        self.add_child(GamePieceType(GamePieceType.DUNGEON_FEATURE))
        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(Description("Fountain",
                                   ("A Fountain full of clean water",
                                    "surely you will become more",
                                    "healthy by drinking this.")))
        self.add_child(GraphicChar(None, colors.CYAN,
                                   symbol.FOUNTAIN_FULL))
        self.add_child(CharPrinter())
        self.add_child(Mover())
        self.add_child(IsDungeonFeature())


class IsDungeonFeature(Leaf):
    """
    Defines that the parent is a dungeon feature.
    """
    def __init__(self):
        super(IsDungeonFeature, self).__init__()
        self.component_type = "is_dungeon_feature"


class DescendStairsAction(action.Action):
    def __init__(self):
        super(DescendStairsAction, self).__init__()
        self.component_type = "descend_stairs_action"
        self.name = "Descend Stairs"
        self.display_order = 50

    def act(self, **kwargs):
        target_entity = kwargs["target_entity"]
        source_entity = kwargs["source_entity"]
        current_dungeon_level = target_entity.dungeon_level.value
        next_dungeon_level = current_dungeon_level.\
            dungeon.get_dungeon_level(current_dungeon_level.depth + 1)
        if(next_dungeon_level is None):
            return False
        destination_position = next_dungeon_level.up_stairs[0].position.value
        target_entity.mover.try_move(destination_position, next_dungeon_level)
        self.add_energy_spent_to_entity(source_entity)
