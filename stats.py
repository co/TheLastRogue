from compositecore import Leaf


class DataPoint(Leaf):
    """
    Class for components holding a single data point.
    """
    def __init__(self, component_type, value):
        super(DataPoint, self).__init__()
        self.component_type = component_type
        self.value = value


class Flag(Leaf):
    """
    Component which only has a component type. Composites with this component has this flag.
    """
    def __init__(self, component_type):
        super(Flag, self).__init__()
        self.component_type = component_type


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
        return self.next.value + self.bonus_value

    @value.setter
    def value(self, new_value):
        self.next.value = new_value


class DataTypes:
    STRENGTH = "strength"
    ARMOR = "armor"
    HIT = "hit"
    STEALTH = "stealth"
    AWARENESS = "awareness"
    EVASION = "evasion"

    MELEE_SPEED = "melee_speed"
    SHOOT_SPEED = "shoot_speed"
    THROW_SPEED = "throw_speed"

    MELEE_DAMAGE_MULTIPLIER = "melee_damage_multiplier"
    THROW_DAMAGE_MULTIPLIER = "throw_damage_multiplier"

    INTELLIGENCE = "intelligence"
    GAME_PIECE_TYPE = "game_piece_type"
    MOVEMENT_SPEED = "movement_speed"
    FACTION = "faction"

    WEIGHT = "weight"
    WEAPON_RANGE = "weapon_range"

    SIGHT_RADIUS = "sight_radius"
    SKIP_ACTION_CHANCE = "skip_action_chance"

    DENSITY = "density"
    CLOUD_TYPE = "cloud_type"
    CLONE_FUNCTION = "clone_function"

    MINIMUM_DEPTH = "minimum_depth"

    GAME_STATE = "game_state"


class Immunities(object):
    SPIDER_WEB = "spider_web_immunity"


class IntelligenceLevel(DataPoint):
    MINDLESS = 0
    PLANT = 1
    ANIMAL = 2
    NORMAL = 3
    HIGH = 4


class Factions(DataPoint):
    PLAYER = 0
    MONSTER = 1


class GamePieceTypes(DataPoint):
    ENTITY = 0
    CLOUD = 1
    ITEM = 2
    DUNGEON_FEATURE = 3
    DUNGEON_TRASH = 4
    TERRAIN = 5

    MAX_INSTANCES_ON_TILE = {ENTITY: 1,
                             CLOUD: 1,
                             ITEM: 1,
                             DUNGEON_FEATURE: 1,
                             DUNGEON_TRASH: 1,
                             TERRAIN: 1}


def max_instances_of_composite_on_tile(composite):
    return GamePieceTypes.MAX_INSTANCES_ON_TILE[composite.game_piece_type.value]


class UnArmedHitTargetEntityEffectFactory(DataPoint):
    def __init__(self, effect_factory_function):
        super(UnArmedHitTargetEntityEffectFactory, self).__init__("unarmed_hit_target_entity_effect_factory_" +
                                                                  str(effect_factory_function), effect_factory_function)
        self.tags.add("unarmed_hit_target_entity_effect_factory")