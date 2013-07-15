import colors
import geometry as geo
import libtcodpy as libtcod


class GamePieceType(object):
    UNDEFINED = 0
    ENTITY = 1
    ITEM = 2
    DUNGEON_FEATURE = 3
    TERRAIN = 4


class GamePiece(object):
    def __init__(self):
        self.__position = geo.Vector2D(-1, -1)
        self.__dungeon_level = None
        self._name = "XXX_unnamed_entity_XXX"
        self._description = "XXX_no_description_XXX"

        #  These fields should both be set by subclasses.
        self.piece_type = GamePieceType.UNDEFINED
        self.max_instances_in_single_tile = -1
        self.draw_order = -1

        self._color_fg = colors.DB_TAHITI_GOLD
        self._color_bg = None
        self._symbol = ord('?')

    @property
    def position(self):
        return self.__position

    @property
    def dungeon_level(self):
        return self.__dungeon_level

    @dungeon_level.setter
    def dungeon_level(self, value):
        self.__dungeon_level = value

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
        copy.__position = self.__position
        copy.dungeon_level = self.dungeon_level
        copy.piece_type = self.piece_type
        copy.max_instances_in_single_tile = self.max_instances_in_single_tile
        copy.draw_order = self.draw_order
        return copy

    def draw(self, is_seen, screen_position):
        x, y = screen_position.x, screen_position.y
        if(not self.color_fg is None):
            if(is_seen):
                fg_color = self.color_fg
            else:
                fg_color = colors.UNSEEN_FG
            libtcod.console_set_char_foreground(0, x, y, fg_color)

        if(not self.color_bg is None):
            if(is_seen):
                bg_color = self.color_bg
            else:
                bg_color = colors.UNSEEN_BG
            libtcod.console_set_char_background(0, x, y, bg_color)
        if(not (self.color_bg is None and
                self.color_fg is None)):
            libtcod.console_set_char(0, x, y, self.symbol)

    def can_move(self, new_position, new_dungeon_level=None):
        if(new_dungeon_level is None):
            new_dungeon_level = self.dungeon_level
        if(not new_dungeon_level.has_tile(new_position)):
            return False
        new_tile = new_dungeon_level.get_tile(new_position)
        if(not self.__can_pass_tile(new_tile)):
            return False
        return True

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
        self.__try_remove_from_dungeon()
        new_place = new_tile.game_pieces[self.piece_type]
        if(len(new_place) < 1):
            new_place.append(self)
        else:
            new_place[0] = self
        self.__position = new_position
        self.dungeon_level = new_dungeon_level

    def __can_pass_tile(self, tile):
        is_too_many = (len(tile.game_pieces[self.piece_type]) >=
                       self.max_instances_in_single_tile)
        if((not is_too_many) and
           self._can_pass_terrain(tile.get_terrain())):
            return True
        return False

    def _can_pass_terrain(self, terrain):
        return True

    def __move(self, new_position, dungeon_level):
        self.__try_remove_from_dungeon()
        new_tile = dungeon_level.get_tile(new_position)
        new_tile.game_pieces[self.piece_type].append(self)
        self.__position = new_position
        self.dungeon_level = dungeon_level

    def try_remove_from_dungeon(self):
        return self.__try_remove_from_dungeon()

    def __try_remove_from_dungeon(self):
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
