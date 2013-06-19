import GamePiece as gamePiece


def tile_copy(tile):
    tile_copy = Tile(tile.terrain)
    tile_copy.game_pieces = tile.game_pieces
    return tile_copy


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
