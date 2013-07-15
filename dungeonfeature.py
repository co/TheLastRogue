import gamepiece
import colors


class DungeonFeature(gamepiece.GamePiece):
    def __init__(self):
        super(DungeonFeature, self).__init__()
        self.piece_type = gamepiece.GamePieceType.ITEM
        self.max_instances_in_single_tile = 1
        self.draw_order = 2
        self.player_actions = []
        self._name = "XXX_UNNAMED_XXX"
        self._description = "XXX_DESCRIPTION_XXX"
        self._color_bg = None

    def try_move(self, new_position, new_dungeon_level=None):
        if(new_dungeon_level is None):
            new_dungeon_level = self.dungeon_level
        old_dungeon_level = self.dungeon_level
        move_succeded = super(DungeonFeature, self).\
            try_move(new_position, new_dungeon_level)
        if(move_succeded):
            if(not old_dungeon_level is None and
               (not old_dungeon_level is new_dungeon_level)):
                old_dungeon_level.remove_dungeon_feature_if_present(self)
            new_dungeon_level.add_dungeon_feature_if_not_present(self)
        return move_succeded

    def try_remove_from_dungeon(self):
        old_dungeon_level = self.dungeon_level
        remove_succeded = super(DungeonFeature, self).\
            try_remove_from_dungeon()
        if(remove_succeded and (not old_dungeon_level is None)):
            old_dungeon_level.remove_dungeon_feature_if_present(self)
        return remove_succeded


class Stairs(DungeonFeature):
    def __init__(self):
        super(Stairs, self).__init__()
        self._color_fg = colors.DB_WHITE


class StairsDown(Stairs):
    def __init__(self):
        super(StairsDown, self).__init__()
        self._symbol = ord('>')
        self._name = "Stairs Down"
        self._description =\
            "A dark passway downward. Oh, what horrors awaits there?"


class StairsUp(Stairs):
    def __init__(self):
        super(StairsUp, self).__init__()
        self._symbol = ord('<')
        self._name = "Stairs Up"
        self._description =\
            "A way back, when the nightmare becomes too real."
