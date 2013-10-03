from composite import Description, GraphicChar
from position import Position
from dungeonlevelcomposite import DungeonLevel
from compositecore import Composite, Leaf
from gamepiecetype import GamePieceType
import symbol
import action
import colors


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
        self.add_child(GraphicChar(symbol.STAIRS_DOWN,
                                   None, colors.WHITE))
        self.add_child(ShareTilePlayerActions(action.DescendStairsAction()))


class StairsUp(Composite):
    """
    Stairs up allows the player to ascend to the next level.
    """
    def __init__(self):
        super(StairsDown, self).__init__()
        self.add_child(GamePieceType(GamePieceType.DUNGEON_FEATURE))
        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(Description("Stairs Up",
                                   ("A way back, when the ",
                                    "nightmare becomes too real.")))
        self.add_child(GraphicChar(symbol.STAIRS_UP,
                                   None, colors.WHITE))
        self.add_child(ShareTilePlayerActions())


class Fountain(Composite):
    """
    Drinking from the fountain makes the player stronger.
    """
    def __init__(self):
        super(StairsDown, self).__init__()
        self.add_child(GamePieceType(GamePieceType.DUNGEON_FEATURE))
        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(Description("Fountain",
                                   ("A Fountain full of clean water",
                                    "surely you will become more",
                                    "healthy by drinking this.")))
        self.add_child(GraphicChar(symbol.STAIRS_UP,
                                   None, colors.WHITE))
        self.add_child(ShareTilePlayerActions())


class ShareTilePlayerActions(Leaf):
    """
    Defines actions that the player may take while sharing tile the parent.
    """
    def __init__(self, actions=[]):
        self.component_type = "share_tile_player_actions"
        self.actions = actions


#class DungeonFeature(gamepiece.GamePiece):
#    def __init__(self):
#        super(DungeonFeature, self).__init__()
#        self.piece_type = gamepiece.GamePieceType.DUNGEON_FEATURE
#        self.max_instances_in_single_tile = 1
#        self.player_actions = []
#        self._name = "XXX_UNNAMED_XXX"
#        self._description = "XXX_DESCRIPTION_XXX"
#        self._color_bg = None
#
#    def try_move(self, new_position, new_dungeon_level=None):
#        if(new_dungeon_level is None):
#            new_dungeon_level = self.dungeon_level
#        old_dungeon_level = self.dungeon_level
#        move_succeded = super(DungeonFeature, self).\
#            try_move(new_position, new_dungeon_level)
#        if(move_succeded):
#            if(not old_dungeon_level is None and
#               (not old_dungeon_level is new_dungeon_level)):
#                old_dungeon_level.remove_dungeon_feature_if_present(self)
#            new_dungeon_level.add_dungeon_feature_if_not_present(self)
#        return move_succeded
#
#    def try_remove_from_dungeon(self):
#        old_dungeon_level = self.dungeon_level
#        remove_succeded = super(DungeonFeature, self).\
#            try_remove_from_dungeon()
#        if(remove_succeded and (not old_dungeon_level is None)):
#            old_dungeon_level.remove_dungeon_feature_if_present(self)
#        return remove_succeded
