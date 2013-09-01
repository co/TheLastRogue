import gamepiece
import frame
import terrain


class Tile(object):
    def __init__(self):
        self.game_pieces = {
            gamepiece.GamePieceType.ENTITY: [],
            gamepiece.GamePieceType.CLOUD: [],
            gamepiece.GamePieceType.ITEM: [],
            gamepiece.GamePieceType.DUNGEON_FEATURE: [],
            gamepiece.GamePieceType.DUNGEON_TRASH: [],
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
        if(color_bg is None):
            self.get_terrain().draw(screen_position)
        piece.draw(screen_position)

    def _draw_unseen(self, screen_position, piece):
        piece.draw_unseen(screen_position)

    def get_first_item(self):
        return self.get_first_piece_of_type(gamepiece.GamePieceType.ITEM)

    def get_first_entity(self):
        return self.get_first_piece_of_type(gamepiece.GamePieceType.ENTITY)

    def get_first_cloud(self):
        return self.get_first_piece_of_type(gamepiece.GamePieceType.CLOUD)

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
