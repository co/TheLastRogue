import colors


class GamePieceType(object):
    UNDEFINED = 0
    ENTITY = 1
    CLOUD = 2
    ITEM = 3
    DUNGEON_FEATURE = 4
    TERRAIN = 5


class GamePiece(object):
    def __init__(self):
        self._position = (-1, -1)
        self._dungeon_level = None
        self._name = "XXX_unnamed_entity_XXX"
        self._description = "XXX_no_description_XXX"

        #  These fields should both be set by subclasses.
        self.piece_type = GamePieceType.UNDEFINED
        self.max_instances_in_single_tile = -1

        self._color_fg = colors.DB_TAHITI_GOLD
        self._color_bg = None
        self._symbol = ord('?')

    @property
    def position(self):
        return self._position

    @property
    def dungeon_level(self):
        return self._dungeon_level

    @dungeon_level.setter
    def dungeon_level(self, value):
        self._dungeon_level = value

    @property
    def color_fg(self):
        return self._color_fg

    @property
    def color_bg(self):
        return self._color_bg

    @property
    def symbol(self):
        return self._symbol

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def piece_copy(self, copy=None):
        if(copy is None):
            copy = self.__class__()
        copy._position = self._position
        copy.dungeon_level = self.dungeon_level
        copy.piece_type = self.piece_type
        copy.max_instances_in_single_tile = self.max_instances_in_single_tile
        return copy

    def can_move(self, new_position, new_dungeon_level=None):
        if(new_dungeon_level is None):
            new_dungeon_level = self.dungeon_level
        if(not new_dungeon_level.has_tile(new_position)):
            return False
        new_tile = new_dungeon_level.get_tile(new_position)
        return (self._can_fit_on_tile(new_tile) and
                self._can_pass_terrain(new_tile.get_terrain()))

    def try_move(self, new_position, new_dungeon_level=None):
        if(new_dungeon_level is None):
            new_dungeon_level = self.dungeon_level
        if(self.can_move(new_position, new_dungeon_level)):
            self.__move(new_position, new_dungeon_level)
            return True
        return False

    def replace_move(self, new_position, new_dungeon_level=None):
        if(new_dungeon_level is None):
            new_dungeon_level = self.dungeon_level
        if(not new_dungeon_level.has_tile(new_position)):
            return False
        new_tile = new_dungeon_level.get_tile(new_position)
        self._try_remove_from_dungeon()
        new_place = new_tile.game_pieces[self.piece_type]
        if(len(new_place) < 1):
            new_place.append(self)
        else:
            new_place[0] = self
        self._position = new_position
        self.dungeon_level = new_dungeon_level

    def _can_fit_on_tile(self, tile):
        return (len(tile.game_pieces[self.piece_type]) <
                self.max_instances_in_single_tile)

    def _can_pass_terrain(self, terrain):
        return True

    def __move(self, new_position, dungeon_level):
        self._try_remove_from_dungeon()
        new_tile = dungeon_level.get_tile(new_position)
        new_tile.game_pieces[self.piece_type].append(self)
        self._position = new_position
        self.dungeon_level = dungeon_level

    def try_remove_from_dungeon(self):
        return self._try_remove_from_dungeon()

    def _try_remove_from_dungeon(self):
        if(self.dungeon_level is None):
            return True
        tile_i_might_be_on = self.dungeon_level.get_tile(self.position)

        pieces_i_might_be_among = \
            tile_i_might_be_on.game_pieces[self.piece_type]

        if(any(self is piece for piece in pieces_i_might_be_among)):
            pieces_i_might_be_among.remove(self)
            self.dungeon_level = None
            return True
        return False
