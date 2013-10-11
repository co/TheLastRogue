from gamepiecetype import GamePieceType
import compositecore
from composite import CharPrinter
import console
import frame
import terrain


class Tile(object):
    def __init__(self):
        self.game_pieces = {
            GamePieceType.ENTITY: [],
            GamePieceType.CLOUD: [],
            GamePieceType.ITEM: [],
            GamePieceType.DUNGEON_FEATURE: [],
            GamePieceType.DUNGEON_TRASH: [],
            GamePieceType.TERRAIN: []
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
        if (pieces[0].game_piece_type.value == GamePieceType.ENTITY):
            animation_length = 7
            cycle_length = len(pieces) * animation_length
            current_animation_frame = frame.current_frame % cycle_length
            return pieces[int(current_animation_frame / animation_length)]
        return pieces[0]

    def _draw_seen(self, screen_position, piece):
        if(piece.graphic_char.color_bg is None):
            self.get_terrain().char_printer.draw(screen_position)
        piece.char_printer.draw(screen_position)

    def _draw_unseen(self, screen_position, piece):
        piece.char_printer.draw_unseen(screen_position)

    def get_first_item(self):
        return self.get_first_piece_of_type(GamePieceType.ITEM)

    def get_first_entity(self):
        return self.get_first_piece_of_type(GamePieceType.ENTITY)

    def get_first_cloud(self):
        return self.get_first_piece_of_type(GamePieceType.CLOUD)

    def get_entities(self):
        return self.game_pieces[GamePieceType.ENTITY]

    def get_terrain(self):
        return self.get_first_piece_of_type(GamePieceType.TERRAIN)

    def get_dungeon_feature(self):
        return self.\
            get_first_piece_of_type(GamePieceType.DUNGEON_FEATURE)

    def get_first_piece_of_type(self, piece_type):
        if(len(self.game_pieces[piece_type]) < 1):
            return None
        return self.game_pieces[piece_type][0]

    def has_entity(self):
        if(len(self.game_pieces[GamePieceType.ENTITY]) < 1):
            return False
        return True

    def copy(self):
        copy = Tile()
        copy.game_pieces = dict()
        for piece_type, piece_list in self.game_pieces.items():
            copy_list = []
            for piece in piece_list:
                new_piece = compositecore.Composite()
                if(piece.has_child("game_piece_type")):
                    new_piece.add_child(piece.game_piece_type.copy())
                if(piece.has_child("graphic_char")):
                    new_piece.add_child(piece.graphic_char.copy())
                if(piece.has_child("description")):
                    new_piece.add_child(piece.description.copy())
                new_piece.add_child(CharPrinter())
                copy_list.append(new_piece)
            copy.game_pieces[piece_type] = copy_list
        return copy


unknown_tile = Tile()
unknown_tile.game_pieces[GamePieceType.TERRAIN]\
    .append(terrain.Unknown())
