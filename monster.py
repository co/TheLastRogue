from actor import DoNothingActor
from attacker import Attacker, Dodger, DamageTypes
from compositecore import Composite, Leaf
from dungeonmask import DungeonMask, Path
from entityeffect import EffectQueue, DissolveDamageEffect, AddSpoofChild
from graphic import CharPrinter, GraphicChar
from health import Health, HealthModifier, BleedWhenDamaged
from inventory import Inventory
from missileaction import MonsterThrowStoneAction, MonsterMagicRangeAction
from monsteractor import ChasePlayerActor, MonsterActorState, HuntPlayerIfHurtMe, KeepPlayerAtDistanceActor
from mover import Mover, Stepper, CanShareTileEntityMover, ImmobileStepper
from ondeath import PrintDeathMessageOnDeath, LeaveCorpseOnDeath, RemoveEntityOnDeath
from position import Position, DungeonLevel
import rng
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
        self.add_child(Mover())
        self.add_child(Stepper())

        self.add_child(EntityMessages("The ratman looks at you.",
                                      "The ratman is beaten to a pulp."))
        self.add_child(Description("Ratman",
                                   "A Rat/Man hybrid it looks hostile."))
        self.add_child(GraphicChar(None, colors.ORANGE, icon.RATMAN))
        self.add_child(CharPrinter())

        self.add_child(Faction(Faction.MONSTER))
        self.add_child(StatusFlags([StatusFlags.CAN_OPEN_DOORS]))
        self.add_child(Health(8))
        self.add_child(HealthModifier())
        self.add_child(MovementSpeed(gametime.single_turn))
        self.add_child(BleedWhenDamaged())

        self.add_child(AttackSpeed())
        self.add_child(Strength(2))
        self.add_child(Attacker())
        self.add_child(Dodger())
        self.add_child(Evasion(16))
        self.add_child(Hit(13))

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
        self.add_child(MonsterThrowStoneAction(30))

        self.add_child(GameState(game_state))
        self.add_child(Equipment())
        self.add_child(Inventory())
        self.add_child(EffectQueue())

        self.add_child(PrintDeathMessageOnDeath())
        self.add_child(LeaveCorpseOnDeath())
        self.add_child(RemoveEntityOnDeath())


class Cyclops(Composite):
    """
    A composite component representing a Cyclops monster.
    """

    def __init__(self, game_state):
        super(Cyclops, self).__init__()
        self.add_child(GamePieceType(GamePieceType.ENTITY))

        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(Mover())
        self.add_child(Stepper())

        self.add_child(EntityMessages("The cyclops looks at you.",
                                      "The cyclops is mangled to the floor."))
        self.add_child(Description("Cyclops",
                                   "A Giant with a single disgusting eye, it's looking for prey."))
        self.add_child(GraphicChar(None, colors.CYAN, icon.CYCLOPS))
        self.add_child(CharPrinter())

        self.add_child(Faction(Faction.MONSTER))
        self.add_child(StatusFlags([StatusFlags.CAN_OPEN_DOORS]))
        self.add_child(Health(40))
        self.add_child(HealthModifier())
        self.add_child(MovementSpeed(gametime.one_and_half_turn))
        self.add_child(BleedWhenDamaged())

        self.add_child(AttackSpeed(gametime.single_turn, throw_speed=gametime.double_turn))
        self.add_child(Strength(12))
        self.add_child(Attacker(0.8, 1.5))
        self.add_child(Dodger())
        self.add_child(Evasion(5))
        self.add_child(Hit(11))

        self.add_child(SightRadius(6))
        self.add_child(DungeonMask())
        self.add_child(Vision())
        self.add_child(Stealth(7))
        self.add_child(Awareness(3))
        self.add_child(AwarenessChecker())

        self.add_child(Path())
        self.add_child(ChasePlayerActor())
        self.add_child(MonsterActorState())
        self.add_child(HuntPlayerIfHurtMe())
        self.add_child(MonsterThrowStoneAction(10, icon=icon.DUNGEON_WALLS_ROW))

        self.add_child(GameState(game_state))
        self.add_child(Equipment())
        self.add_child(Inventory())
        self.add_child(EffectQueue())

        self.add_child(PrintDeathMessageOnDeath())
        self.add_child(LeaveCorpseOnDeath())
        self.add_child(RemoveEntityOnDeath())


class Jericho(Ratman):
    def __init__(self, game_state):
        super(Jericho, self).__init__(game_state)
        self.description.name = "Jericho"
        self.entity_messages.death_message = "Jericho the quick is no more."
        self.graphic_char.color_fg = colors.YELLOW
        self.actor.energy_recovery = gametime.double_energy_gain


class Ghost(Composite):
    """
    A composite component representing a Ghost monster.
    """

    def __init__(self, game_state):
        super(Ghost, self).__init__()
        self.add_child(GamePieceType(GamePieceType.ENTITY))

        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(Mover())
        self.add_child(Stepper())

        self.add_child(EntityMessages("The ghost sees you.",
                                      "The ghost fades away."))
        self.add_child(Description("Ghost",
                                   "A spirit of a hunted creature."))
        self.add_child(GraphicChar(None, colors.BLUE, icon.GHOST))
        self.add_child(CharPrinter())

        self.add_child(Faction(Faction.MONSTER))
        self.add_child(StatusFlags([StatusFlags.CAN_OPEN_DOORS, StatusFlags.FLYING]))
        self.add_child(Health(1))
        self.add_child(HealthModifier())
        self.add_child(MovementSpeed(gametime.single_turn + gametime.one_third_turn))

        self.add_child(AttackSpeed())
        self.add_child(Strength(2))
        self.add_child(Attacker())
        self.add_child(Dodger())
        self.add_child(Evasion(22))
        self.add_child(Hit(14))

        self.add_child(SightRadius(6))
        self.add_child(DungeonMask())
        self.add_child(Vision())
        self.add_child(Stealth(7))
        self.add_child(Awareness(8))
        self.add_child(AwarenessChecker())

        self.add_child(Path())
        self.add_child(KeepPlayerAtDistanceActor(4))
        self.add_child(MonsterActorState())
        self.add_child(HuntPlayerIfHurtMe())

        self.add_child(MonsterMagicRangeAction(1, 60))
        self.add_child(GameState(game_state))
        self.add_child(Equipment())
        self.add_child(Inventory())
        self.add_child(EffectQueue())
        self.add_child(AddGhostReviveToSeenEntities())

        self.add_child(PrintDeathMessageOnDeath())
        self.add_child(RemoveEntityOnDeath())


class AddGhostReviveToSeenEntities(Leaf):
    """
    Revive other living creatures as ghosts.
    """
    def __init__(self):
        super(AddGhostReviveToSeenEntities, self).__init__()
        self.component_type = "add_ghost_revive_to_seen_entities"

    def before_tick(self, time):
        seen_entities = self.parent.vision.get_seen_entities()
        for entity in seen_entities:
            if not isinstance(entity, Ghost):
                effect = ReviveAsGhostOnDeath()
                entity.effect_queue.add(AddSpoofChild(self.parent, effect, 1))


class ReviveAsGhostOnDeath(Leaf):
    """
    Will remove the parent from the dungeon when parent Entity dies.
    """
    def __init__(self):
        super(ReviveAsGhostOnDeath, self).__init__()
        self.component_type = "revive_as_ghost_on_death"

    def on_tick(self, time):
        if self.parent.health.is_dead():
            ghost = Ghost(self.parent.game_state.value)
            ghost.mover.try_move_roll_over(self.parent.position.value,
                                           self.parent.dungeon_level.value)


class StoneStatue(Composite):
    """
    A composite component representing a Ratman monster.
    """

    def __init__(self, game_state):
        super(StoneStatue, self).__init__()
        self.add_child(GamePieceType(GamePieceType.ENTITY))

        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(Mover())
        self.add_child(Stepper())

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

        self.add_child(Faction(Faction.MONSTER))
        self.add_child(Health(30))
        self.add_child(HealthModifier())

        self.add_child(Strength(0))
        self.add_child(MovementSpeed(gametime.single_turn))
        self.add_child(AttackSpeed(gametime.single_turn))
        self.add_child(StatusFlags([StatusFlags.CAN_OPEN_DOORS]))
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
        self.add_child(Attacker())

        self.add_child(PrintDeathMessageOnDeath())
        self.add_child(LeaveCorpseOnDeath())
        self.add_child(RemoveEntityOnDeath())


class Slime(Composite):
    """
    A composite component representing a Ratman monster.
    """

    def __init__(self, game_state):
        super(Slime, self).__init__()
        self.add_child(GamePieceType(GamePieceType.ENTITY))

        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(Stepper())
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

        self.add_child(Faction(Faction.MONSTER))
        self.add_child(Health(40))
        self.add_child(HealthModifier())

        self.add_child(Strength(2))
        self.add_child(MovementSpeed(gametime.single_turn + gametime.one_third_turn))
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

        self.add_child(EntityShareTileEffect(DissolveEntitySlimeShareTileEffect()))

        self.add_child(PrintDeathMessageOnDeath())
        self.add_child(RemoveEntityOnDeath())


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
            self.effect(source_entity=self.parent, target_entity=sharing_entity, time=time_spent)


class DissolveEntitySlimeShareTileEffect(object):
    def __init__(self):
        pass

    def __call__(self, **kwargs):
        target_entity = kwargs["target_entity"]
        source_entity = kwargs["source_entity"]
        strength = source_entity.strength.value
        damage = rng.random_variance(strength, 1)

        dissolve_effect = DissolveDamageEffect(source_entity, damage, [DamageTypes.ACID], gametime.single_turn)
        target_entity.effect_queue.add(dissolve_effect)

        stuck_in_slime_step_spoof = StuckInSlimeStepperSpoof(source_entity)
        add_spoof_effect = AddSpoofChild(source_entity, stuck_in_slime_step_spoof, time_to_live=1)
        target_entity.effect_queue.add(add_spoof_effect)


class StuckInSlimeStepperSpoof(Stepper):
    def __init__(self, slime):
        super(StuckInSlimeStepperSpoof, self).__init__()
        self.component_type = "stepper"
        self._slime = slime

    def try_move_or_bump(self, position):
        my_strength = self.parent.strength.value
        slime_strength = self._slime.strength.value
        if self.has_sibling("attacker"):
            self.parent.attacker.hit(self._slime)
        if rng.stat_check(my_strength, slime_strength + 4):
            self._make_slime_skip_turn()
            return self.next.try_move_or_bump(position)
        return self.parent.movement_speed.value

    def _make_slime_skip_turn(self):
        immobile_stepper = ImmobileStepper()
        add_spoof_effect = AddSpoofChild(self.parent, immobile_stepper, gametime.single_turn)
        self._slime.effect_queue.add(add_spoof_effect)
