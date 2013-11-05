from compositecore import Leaf


class Strength(Leaf):
    """
    Composites holding this has the strength attribute.
    """
    def __init__(self, strength):
        super(Strength, self).__init__()
        self.component_type = "strength"
        self.value = strength


class IsPlayer(Leaf):
    """
    Component that marks the player.

    Only the player should have this component.
    """
    def __init__(self):
        super(IsPlayer, self).__init__()
        self.component_type = "is_player"


class Hit(Leaf):
    """
    A value determining how likely you are to hit something.
    """
    def __init__(self, hit):
        super(Hit, self).__init__()
        self.component_type = "hit"
        self.value = hit


class Evasion(Leaf):
    """
    High evasion means parent entity is harder to hit.
    """
    def __init__(self, evasion):
        super(Evasion, self).__init__()
        self.component_type = "evasion"
        self.value = evasion


class AttackSpeed(Leaf):
    """
    Composites holding this has the attack_speed attribute.
    """
    def __init__(self, attack_speed):
        super(AttackSpeed, self).__init__()
        self.attack_speed = attack_speed
        self.component_type = "attack_speed"


class GameState(Leaf):
    """
    Composites holding this has the attack_speed attribute.
    """
    def __init__(self, value):
        super(GameState, self).__init__()
        self.value = value
        self.component_type = "game_state"


class MovementSpeed(Leaf):
    """
    Composites holding this has the attack_speed attribute.
    """
    def __init__(self, value):
        super(MovementSpeed, self).__init__()
        self.value = value
        self.component_type = "movement_speed"


class Faction(Leaf):
    """
    The faction attribute keeps track of the faction.

    All other factions are concidered hostile.
    """

    PLAYER = 0
    MONSTER = 1

    def __init__(self, faction):
        super(Faction, self).__init__()
        self.component_type = "faction"
        self.value = faction


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
        self.component_type = "game_piece_type"
        self.value = piece_type

    @property
    def max_instances_in_tile(self):
        return self.__class__.\
            _MAX_INSTANCES_OF_PIECE_TYPE_ON_TILE[self.value]

    def copy(self):
        """
        Makes a copy of this component.
        """
        return GamePieceType(self.value)
