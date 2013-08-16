import gamepiece
import symbol
import action
import colors


class DungeonFeature(gamepiece.GamePiece):
    def __init__(self):
        super(DungeonFeature, self).__init__()
        self.piece_type = gamepiece.GamePieceType.DUNGEON_FEATURE
        self.max_instances_in_single_tile = 1
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
        self._symbol = symbol.STAIRS_DOWN
        self._name = "Stairs Down"
        self._description =\
            "A dark passway downward. Oh, what horrors awaits there?"
        self.player_actions.append(action.DescendStairsAction())


class StairsUp(Stairs):
    def __init__(self):
        super(StairsUp, self).__init__()
        self._symbol = symbol.STAIRS_UP
        self._name = "Stairs Up"
        self._description =\
            "A way back, when the nightmare becomes too real."


class Fountain(DungeonFeature):
    def __init__(self, drinks_left):
        super(Fountain, self).__init__()
        self._drinks_left = drinks_left
        self._name = "Fountain"
        self._description_full =\
                "A Fountain full of clean water, surely you will become more healthy by drinking this."
        self._description_empty =\
                "Once there was clean water here, but it has since dried up."

    @property
    def symbol(self):
        if self._drinks_left > 0:
            return symbol.FOUNTAIN_FULL
        else:
            return symbol.FOUNTAIN_EMPTY

    @property
    def color_fg(self):
        if self._drinks_left > 0:
            return colors.DB_VIKING
        else:
            return colors.DB_HEATHER


    @property
    def description(self):
        if self._drinks_left > 0:
            return symbol.FOUNTAIN_FULL
        else:
            return symbol.FOUNTAIN_EMPTY
