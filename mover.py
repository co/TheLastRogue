from composite import Leaf, DungeonLevel, GamePieceType, Position, StatusFlags
from terrain import Door


class Mover(Leaf):
    """
    Component for moving and checking if a move is legal.
    """

    def can_move(self, new_position, new_dungeon_level=None):
        """
        Checks if parent comoponent can move to new position.
        """
        if(new_dungeon_level is None):
            new_dungeon_level =\
                self.get_sibling_of_type(DungeonLevel).dungeon_level
        if(not new_dungeon_level.has_tile(new_position)):
            return False
        new_tile = new_dungeon_level.get_tile(new_position)
        return (self._can_fit_on_tile(new_tile) and
                self._can_pass_terrain(new_tile.get_terrain()))

    def try_move(self, new_position, new_dungeon_level=None):
        """
        Tries to move parent to new position.

        Returns true if it is successful, false otherwise.
        """
        if(new_dungeon_level is None):
            new_dungeon_level =\
                self.get_sibling_of_type(DungeonLevel).dungeon_level
        if(self.can_move(new_position, new_dungeon_level)):
            self._move(new_position, new_dungeon_level)
            return True
        return False

    def _move(self, new_position, dungeon_level):
        """
        Moves parent to new position, assumes that it fits there.
        """
        self.try_remove_from_dungeon()
        new_tile = dungeon_level.get_tile(new_position)
        piece_type = self.get_sibling_of_type(GamePieceType).value
        new_tile.game_pieces[piece_type].append(self.parent)
        print new_tile.game_pieces
        self.get_sibling_of_type(Position).position = new_position
        dungeon_level_module = DungeonLevel()
        dungeon_level_module.dungeon_level = dungeon_level
        self.parent.add_child(dungeon_level_module)

    def replace_move(self, new_position, new_dungeon_level=None):
        """
        Moves parent to new position and replaces what was already there.
        """
        if(new_dungeon_level is None):
            new_dungeon_level =\
                self.get_sibling_of_type(DungeonLevel).dungeon_level
        if(not new_dungeon_level.has_tile(new_position)):
            return False
        new_tile = new_dungeon_level.get_tile(new_position)
        self.try_remove_from_dungeon()
        piece_type = self.get_sibling_of_type(GamePieceType).value
        new_place = new_tile.game_pieces[piece_type]
        for piece in new_place:
            piece.get_child_of_type(Mover).try_remove_from_dungeon()
        self.try_move(new_position, new_dungeon_level)

    def _can_fit_on_tile(self, tile):
        """
        Checks if the parent can fit on the tile.
        """
        piece_type = self.get_sibling_of_type(GamePieceType)
        return (len(tile.game_pieces[piece_type.value]) <
                piece_type.max_instances_in_tile)

    def _can_pass_terrain(self, terrain_to_pass):
        """
        Checks if the parent can move through a terrain.
        """
        if(terrain_to_pass is None):
            return False
        if(not terrain_to_pass.is_solid()):
            return True
        status_flags = self.get_sibling_of_type(StatusFlags)
        if(not status_flags is None and
           status_flags.has_status(StatusFlags.CAN_OPEN_DOORS) and
           isinstance(terrain_to_pass, Door)):
            return True
        return False

    def try_remove_from_dungeon(self):
        """
        Tries to remove parent from dungeon.
        """
        if(not self.has_sibling(DungeonLevel)):
            return True
        position = self.get_sibling_of_type(Position).position
        tile_i_might_be_on = (self.get_sibling_of_type(DungeonLevel).
                              dungeon_level.get_tile(position))

        piece_type = self.get_sibling_of_type(GamePieceType).value
        pieces_i_might_be_among = \
            tile_i_might_be_on.game_pieces[piece_type]
        if self.has_sibling(DungeonLevel):
            self.parent.remove_child_of_type(DungeonLevel)
        if(any(self.parent is piece for piece in pieces_i_might_be_among)):
            pieces_i_might_be_among.remove(self.parent)
            return True
        return False
