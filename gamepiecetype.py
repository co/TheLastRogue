from compositecore import Leaf


class GamePieceType(Leaf):
    ENTITY = 0
    CLOUD = 1
    ITEM = 2
    DUNGEON_FEATURE = 3
    DUNGEON_TRASH = 4
    TERRAIN = 5

    _MAX_INSTANCES_OF_PIECE_TYPE_ON_TILE = {ENTITY: 1,
                                            CLOUD: 1,
                                            ITEM: 1,
                                            DUNGEON_FEATURE: 1,
                                            DUNGEON_TRASH: 1,
                                            TERRAIN: 1}

    def __init__(self, piece_type=None):
        super(GamePieceType, self).__init__()
        self.value = piece_type

    @property
    def max_instances_in_tile(self):
        return self.__class__.\
            _MAX_INSTANCES_OF_PIECE_TYPE_ON_TILE[self.value]
