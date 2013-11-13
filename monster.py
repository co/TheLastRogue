from action import PickUpItemAction
from actor import DoNothingActor
from attacker import Attacker, Dodger, Damage, DamageTypes
from compositecore import Composite, Leaf
from dungeonmask import DungeonMask, Path
from entityeffect import EffectQueue
from graphic import CharPrinter, GraphicChar
from health import Health, HealthModifier, BleedWhenDamaged
from inventory import Inventory
from missileaction import MonsterThrowRockAction
from monsteractor import ChasePlayerActor, MonsterActorState, HuntPlayerIfHurtMe
from mover import EntityMover, CanShareTileEntityMover
from ondeathaction import EntityDeathAction
from position import Position, DungeonLevel
from stats import AttackSpeed, Faction, GameState, Evasion, Stealth, Awareness
from stats import MovementSpeed, Strength, GamePieceType, Hit
from statusflags import StatusFlags
from text import Description, EntityMessages
from vision import Vision, SightRadius, AwarenessChecker
import colors
from equipment import Equipment
import gametime
import icon


class Ratman(Composite):
    """
    A composite component representing a Ratman monster.
    """

    def __init__(self, game_state):
        super(Ratman, self).__init__()
        self.add_child(GamePieceType(GamePieceType.ENTITY))

        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(EntityMover())

        self.add_child(EntityMessages("The ratman looks at you.",
                                      "The ratman is beaten to a pulp."))
        self.add_child(Description("Ratman",
                                   "A Rat/Man hybrid it looks hostile."))
        self.add_child(GraphicChar(None, colors.ORANGE, icon.RATMAN))
        self.add_child(CharPrinter())
        self.add_child(EntityDeathAction())

        self.add_child(Faction(Faction.MONSTER))
        self.add_child(StatusFlags([StatusFlags.LEAVES_CORPSE,
                                    StatusFlags.CAN_OPEN_DOORS]))
        self.add_child(Health(10))
        self.add_child(HealthModifier())
        self.add_child(MovementSpeed(gametime.single_turn))
        self.add_child(BleedWhenDamaged())

        self.add_child(AttackSpeed(gametime.single_turn))
        self.add_child(Strength(2))
        self.add_child(Attacker())
        self.add_child(Dodger())
        self.add_child(Evasion(12))
        self.add_child(Hit(15))

        self.add_child(SightRadius(6))
        self.add_child(DungeonMask())
        self.add_child(Vision())
        self.add_child(Stealth(7))
        self.add_child(Awareness(5))
        self.add_child(AwarenessChecker())

        self.add_child(Path())
        self.add_child(ChasePlayerActor())
        self.add_child(MonsterActorState())
        self.add_child(HuntPlayerIfHurtMe())
        self.add_child(MonsterThrowRockAction())

        self.add_child(GameState(game_state))
        self.add_child(Equipment())
        self.add_child(Inventory())
        self.add_child(EffectQueue())
        self.add_child(PickUpItemAction())


class Jerico(Ratman):
    def __init__(self, game_state):
        super(Jerico, self).__init__(game_state)
        self.description.name = "Jerico"
        self.entity_messages.death_message = "Jerico the quick is no more."
        self.graphic_char.color_fg = colors.YELLOW
        self.actor.energy_recovery = gametime.double_energy_gain


class StoneStatue(Composite):
    """
    A composite component representing a Ratman monster.
    """

    def __init__(self, game_state):
        super(StoneStatue, self).__init__()
        self.add_child(GamePieceType(GamePieceType.ENTITY))

        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(EntityMover())

        self.add_child(EntityMessages(("The stone statue casts a"
                                       "long shadow on the floor."),
                                      ("The stone statue shatters pieces, "
                                       "sharp rocks covers the ground.")))
        self.add_child(Description("Stone Statue",
                                   ("A Statue made out of stone stands tall."
                                    "It seems to be looking at you...")))
        self.add_child(GraphicChar(None, colors.GRAY,
                                   icon.GOLEM))
        self.add_child(CharPrinter())
        self.add_child(EntityDeathAction())

        self.add_child(Faction(Faction.MONSTER))
        self.add_child(Health(30))
        self.add_child(HealthModifier())

        self.add_child(Strength(0))
        self.add_child(MovementSpeed(gametime.single_turn))
        self.add_child(AttackSpeed(gametime.single_turn))
        self.add_child(StatusFlags([StatusFlags.LEAVES_CORPSE,
                                    StatusFlags.CAN_OPEN_DOORS]))
        self.add_child(Dodger())
        self.add_child(Evasion(0))
        self.add_child(Hit(0))

        self.add_child(SightRadius(6))
        self.add_child(DungeonMask())
        self.add_child(Vision())
        self.add_child(Stealth(7))
        self.add_child(Awareness(5))
        self.add_child(AwarenessChecker())

        self.add_child(Inventory())
        self.add_child(Path())
        self.add_child(DoNothingActor())
        self.add_child(GameState(game_state))
        self.add_child(Equipment())
        self.add_child(EffectQueue())
        self.add_child(PickUpItemAction())
        self.add_child(Attacker())


class Slime(Composite):
    """
    A composite component representing a Ratman monster.
    """

    def __init__(self, game_state):
        super(Slime, self).__init__()
        self.add_child(GamePieceType(GamePieceType.ENTITY))

        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(CanShareTileEntityMover())

        self.add_child(EntityMessages(("The slime seems to",
                                       "wobble with happiness."),
                                      "The slime melts away."))
        self.add_child(Description("Slime",
                                   ("Slime, slime, slime. Ugh, I hate Slimes."
                                    "It seems to be looking at you...")))
        self.add_child(GraphicChar(None, colors.GREEN,
                                   icon.SLIME))
        self.add_child(CharPrinter())
        self.add_child(EntityDeathAction())

        self.add_child(Faction(Faction.MONSTER))
        self.add_child(Health(20))
        self.add_child(HealthModifier())

        self.add_child(Strength(6))
        self.add_child(MovementSpeed(gametime.double_turn))
        self.add_child(AttackSpeed(gametime.single_turn))
        self.add_child(StatusFlags())
        self.add_child(Dodger())
        self.add_child(Evasion(7))
        self.add_child(Hit(15))
        self.add_child(Stealth(7))
        self.add_child(Awareness(5))
        self.add_child(AwarenessChecker())

        self.add_child(SightRadius(6))
        self.add_child(DungeonMask())
        self.add_child(Vision())
        self.add_child(Stealth(7))
        self.add_child(Awareness(5))
        self.add_child(AwarenessChecker())

        self.add_child(Inventory())
        self.add_child(Path())
        self.add_child(ChasePlayerActor())
        self.add_child(MonsterActorState())
        self.add_child(HuntPlayerIfHurtMe())

        self.add_child(GameState(game_state))
        self.add_child(Equipment())
        self.add_child(EffectQueue())
        self.add_child(PickUpItemAction())

        self.add_child(EntityShareTileEffect
            (DissolveEntitySlimeShareTileEffect()))


class EntityShareTileEffect(Leaf):
    """
    Defines an effect that sharing tile with this parent entity will result in.
    """

    def __init__(self, effect):
        super(EntityShareTileEffect, self).__init__()
        self.component_type = "entity_share_tile_effect"
        self.effect = effect

    def share_tile_effect_tick(self, sharing_entity, time_spent):
        if not sharing_entity is self.parent:
            self.effect(source_entity=self.parent,
                        target_entity=sharing_entity,
                        time=time_spent)


class DissolveEntitySlimeShareTileEffect(object):
    def __init__(self):
        pass

    def __call__(self, **kwargs):
        target_entity = kwargs["target_entity"]
        source_entity = kwargs["source_entity"]
        time = kwargs["time"]
        strength = source_entity.strength.value
        damage = Damage(strength, strength / 3,
                        [DamageTypes.ACID, DamageTypes.PHYSICAL],
                        time / gametime.single_turn)
        damage.damage_entity(source_entity, target_entity)
