import colors
import vector2d
import libtcodpy as libtcod


UNDEFINED_GAME_PIECE = 0
ENTITY_GAME_PIECE = 1
ITEM_GAME_PIECE = 2
DECORATION_GAME_PIECE = 3


class GamePiece(object):
    def __init__(self):
        self.__position = vector2d.Vector2D(-1, -1)
        self.__dungeon_level = None
        self.name = "XXX_unnamed_entity_XXX"

        #  These fields should both be set by subclasses.
        self.piece_type = UNDEFINED_GAME_PIECE
        self.max_instances_in_single_tile = -1
        self.draw_order = -1

    @property
    def position(self):
        return self.__position

    @property
    def dungeon_level(self):
        return self.__dungeon_level

    @dungeon_level.setter
    def dungeon_level(self, value):
        self.__dungeon_level = value

    @staticmethod
    def get_color_fg():
        return colors.UNINITIALIZED_FG

    @staticmethod
    def get_color_bg():
        return None

    @staticmethod
    def get_symbol():
        return ord('?')

    def piece_copy(self, copy=None):
        if(copy is None):
            copy = self.__class__()
        copy.__position = self.__position
        copy.dungeon_level = self.dungeon_level
        copy.piece_type = self.piece_type
        copy.max_instances_in_single_tile = self.max_instances_in_single_tile
        copy.draw_order = self.draw_order
        return copy

    def draw(self, is_seen, camera):
        position = self.position + camera.offset
        if(not self.get_color_fg() is None):
            if(is_seen):
                fg_color = self.get_color_fg()
            else:
                fg_color = colors.UNSEEN_FG
            libtcod.console_set_char_foreground(0, position.x,
                                                position.y, fg_color)

        if(not self.get_color_bg() is None):
            libtcod.console_set_char_foreground(0, position.x,
                                                position.y,
                                                self.get_color_bg())
        if(not (self.get_color_bg() is None and
                self.get_color_fg() is None)):
            libtcod.console_set_char(0, position.x, position.y,
                                     self.get_symbol())

    def try_move(self, new_position, new_dungeon_level=None):
        if(new_dungeon_level is None):
            new_dungeon_level = self.dungeon_level
        new_tile = new_dungeon_level.get_tile(new_position)
        if(not self.__can_place_piece_on_tile(new_tile)):
            return False
        self.__move(new_dungeon_level, new_position)
        return True

    def __can_place_piece_on_tile(self, tile):
        return((len(tile.game_pieces[self.piece_type]) <
                self.max_instances_in_single_tile) and
               not tile.terrain.is_solid())

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

    def __move(self, dungeon_level, new_position):
        self.__try_remove_from_dungeon()
        new_tile = dungeon_level.get_tile(new_position)
        new_tile.game_pieces[self.piece_type].append(self)
        self.__position = new_position
        self.dungeon_level = dungeon_level
