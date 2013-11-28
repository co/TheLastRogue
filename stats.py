from compositecore import Leaf
import gametime


class DataPoint(Leaf):
    """
    Base class for components holding a single data point.
    """
    def __init__(self, component_type, value):
        super(DataPoint, self).__init__()
        self.component_type = component_type
        self.value = value


class DataPointBonusSpoof(Leaf):
    """
    Defines a bonus value, if this is added to an entity as spoof.
    The entity will get that bonus added to the normal value.
    """
    def __init__(self, component_type, bonus_value):
        super(DataPointBonusSpoof, self).__init__()
        self.component_type = component_type
        self.bonus_value = bonus_value

    @property
    def value(self):
        print self.component_type, self.bonus_value
        return self.next.value + self.bonus_value

    @value.setter
    def value(self, new_value):
        self.next.value = new_value


class Strength(DataPoint):
    """
    Composites holding this has the strength attribute.
    """
    def __init__(self, strength):
        super(Strength, self).__init__("strength", strength)


class IsPlayer(Leaf):
    """
    Component that marks the player.

    Only the player should have this component.
    """
    def __init__(self):
        super(IsPlayer, self).__init__()
        self.component_type = "is_player"


class Hit(DataPoint):
    """
    A value determining how likely you are to hit something.
    """
    def __init__(self, hit):
        super(Hit, self).__init__("hit", hit)


class Stealth(DataPoint):
    """
    A value determining how good you are to go unnoticed.
    """
    def __init__(self, stealth):
        super(Stealth, self).__init__("stealth", stealth)


class Awareness(DataPoint):
    """
    A value determining how good you are to noticing things.
    """
    def __init__(self, awareness):
        super(Awareness, self).__init__("awareness", awareness)


class Evasion(DataPoint):
    """
    High evasion means parent entity is harder to hit.
    """
    def __init__(self, evasion):
        super(Evasion, self).__init__("evasion", evasion)


class AttackSpeed(Leaf):
    """
    Composites holding this has the attack_speed attribute.
    """
    def __init__(self, melee_speed=gametime.single_turn, throw_speed=gametime.single_turn, shoot_speed=gametime.single_turn):
        super(AttackSpeed, self).__init__()
        self.component_type = "attack_speed"
        self.melee = melee_speed
        self.throw = throw_speed
        self.shoot = shoot_speed


class GameState(DataPoint):
    """
    Composites holding this has the attack_speed attribute.
    """
    def __init__(self, value):
        super(GameState, self).__init__("game_state", value)


class MovementSpeed(DataPoint):
    """
    Composites holding this has the attack_speed attribute.
    """
    def __init__(self, value):
        super(MovementSpeed, self).__init__("movement_speed", value)


class Faction(DataPoint):
    """
    The faction attribute keeps track of the faction.

    All other factions are considered hostile.
    """

    PLAYER = 0
    MONSTER = 1

    def __init__(self, faction):
        super(Faction, self).__init__("faction", faction)


class GamePieceType(DataPoint):
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
        super(GamePieceType, self).__init__("game_piece_type", piece_type)

    @property
    def max_instances_in_tile(self):
        return self.__class__.\
            _MAX_INSTANCES_OF_PIECE_TYPE_ON_TILE[self.value]

    def copy(self):
        """
        Makes a copy of this component.
        """
        return GamePieceType(self.value)
