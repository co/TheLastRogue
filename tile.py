import gamepiece
import frame
import terrain
import colors
import console


class Tile(object):
    def __init__(self):
        self.game_pieces = {
            gamepiece.GamePieceType.ENTITY: [],
            gamepiece.GamePieceType.ITEM: [],
            gamepiece.GamePieceType.DUNGEON_FEATURE: [],
            gamepiece.GamePieceType.TERRAIN: []
        }

    def draw(self, screen_position, is_seen):
        piece = self.get_piece_to_draw()
        if(is_seen):
            self._draw_seen(screen_position, piece)
        else:
            self._draw_unseen(screen_position, piece)

    def get_piece_to_draw(self):
        pieces = next(list for list in self.game_pieces.values()
                      if len(list) > 0)
        if (pieces[0].piece_type == gamepiece.GamePieceType.ENTITY):
            animation_length = 7
            cycle_length = len(pieces) * animation_length
            current_animation_frame = frame.current_frame % cycle_length
            return pieces[int(current_animation_frame / animation_length)]
        return pieces[0]

    def _draw_seen(self, screen_position, piece):
        color_bg = piece.color_bg
        color_fg = piece.color_fg
        if(color_bg is None):
            color_bg = self.get_terrain().color_bg
        console.console.set_colors_and_symbol(screen_position, color_fg,
                                              color_bg, piece.symbol)

    def _draw_unseen(self, screen_position, piece):
        console.console.set_colors_and_symbol(screen_position,
                                              colors.UNSEEN_FG,
                                              colors.UNSEEN_BG, piece.symbol)

    def __non_empty_pieces_lists_sorted_on_draw_order(self):
        piece_lists = self.game_pieces.values()
        non_empty_piece_lists = filter(lambda pl: pl != [], piece_lists)
        lists_sorted_on_draw_order = sorted(non_empty_piece_lists,
                                            key=lambda piece_list:
                                            piece_list[0].draw_order)
        return lists_sorted_on_draw_order

    def get_first_item(self):
        return self.get_first_piece_of_type(gamepiece.GamePieceType.ITEM)

    def get_first_entity(self):
        return self.get_first_piece_of_type(gamepiece.GamePieceType.ENTITY)

    def get_entities(self):
        return self.game_pieces[gamepiece.GamePieceType.ENTITY]

    def get_terrain(self):
        return self.get_first_piece_of_type(gamepiece.GamePieceType.TERRAIN)

    def get_dungeon_feature(self):
        return self.\
            get_first_piece_of_type(gamepiece.GamePieceType.DUNGEON_FEATURE)

    def get_first_piece_of_type(self, piece_type):
        if(len(self.game_pieces[piece_type]) < 1):
            return None
        return self.game_pieces[piece_type][0]

    def has_entity(self):
        if(len(self.game_pieces[gamepiece.GamePieceType.ENTITY]) < 1):
            return False
        return True

    def copy(self):
        copy = Tile()
        copy.game_pieces = dict()
        for piece_type, piece_list in self.game_pieces.items():
            copy.game_pieces[piece_type] =\
                [piece.piece_copy() for piece in piece_list]
        return copy


unknown_tile = Tile()
unknown_tile.game_pieces[gamepiece.GamePieceType.TERRAIN]\
    .append(terrain.Unknown())
