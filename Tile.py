import GamePiece as gamePiece


class Tile(object):
    def __init__(self, terrain):
        self.terrain = terrain
        self.game_pieces = {
            gamePiece.ENTITY_GAME_PIECE: [],
            gamePiece.ITEM_GAME_PIECE: [],
            gamePiece.DECORATION_GAME_PIECE: []
        }

    def draw(self, position, is_seen):
        self.terrain.draw(position, is_seen)
        for piece_list in self.__pieces_lists_sorted_on_draw_order():
            for piece in piece_list:
                piece.draw(is_seen)

    def __pieces_lists_sorted_on_draw_order(self):
        piece_lists = self.game_pieces.values()
        non_empty_piece_lists = filter(lambda pl: pl != [], piece_lists)
        lists_sorted_on_draw_order = sorted(non_empty_piece_lists,
                                            key=lambda piece_list:
                                            piece_list[0].draw_order)
        return lists_sorted_on_draw_order

    def copy(self):
        copy = Tile(self.terrain)
        copy.game_pieces = dict()
        for piece_type, piece_list in self.game_pieces.items():
            copy.game_pieces[piece_type] =\
                [piece.piece_copy() for piece in piece_list]
        return copy
