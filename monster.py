import random
from attacker import Attacker, Dodger, DamageTypes, ArmorChecker
from compositecore import Composite, Leaf
import constants
from dungeonmask import DungeonMask, Path
from entityeffect import EffectQueue, AddSpoofChild, EffectStackID, UndodgeableDamagAndBlockSameEffect, DamageOverTimeEffect
from graphic import CharPrinter, GraphicChar
from health import Health, HealthModifier, BleedWhenDamaged
from inventory import Inventory
import messenger
from missileaction import MonsterThrowStoneAction, MonsterMagicRangeAction
from monsteractor import ChasePlayerActor, MonsterActorState, HuntPlayerIfHurtMe, KeepPlayerAtDistanceActor
from mover import Mover, Stepper, SlimeCanShareTileEntityMover, ImmobileStepper
from ondeath import PrintDeathMessageOnDeath, LeaveCorpseOnDeath, RemoveEntityOnDeath
from position import Position, DungeonLevel
import rng
from stats import Flag, UnArmedHitTargetEntityEffectFactory, DataPoint, DataTypes, Factions, IntelligenceLevels
from stats import GamePieceTypes
from statusflags import StatusFlags
from text import Description, EntityMessages
from vision import Vision, AwarenessChecker
import colors
from equipment import Equipment
import gametime
import icon


def set_monster_components(monster, game_state):
    monster.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.ENTITY))
    monster.set_child(DataPoint(DataTypes.MOVEMENT_SPEED, gametime.single_turn))
    monster.set_child(DataPoint(DataTypes.MELEE_SPEED, gametime.single_turn))
    monster.set_child(DataPoint(DataTypes.THROW_SPEED, gametime.single_turn))
    monster.set_child(DataPoint(DataTypes.SHOOT_SPEED, gametime.single_turn))
    monster.set_child(DataPoint(DataTypes.SIGHT_RADIUS, constants.COMMON_SIGHT_RADIUS))
    monster.set_child(DataPoint(DataTypes.FACTION, Factions.MONSTER))
    monster.set_child(DataPoint(DataTypes.GAME_STATE, game_state))
    monster.set_child(DataPoint(DataTypes.INTELLIGENCE, IntelligenceLevels.NORMAL))

    monster.set_child(Position())
    monster.set_child(CharPrinter())
    monster.set_child(DungeonLevel())

    monster.set_child(Mover())
    monster.set_child(Stepper())

    monster.set_child(HealthModifier())
    monster.set_child(Dodger())
    monster.set_child(ArmorChecker())
    monster.set_child(AwarenessChecker())
    monster.set_child(DungeonMask())
    monster.set_child(Vision())
    monster.set_child(Path())
    monster.set_child(ChasePlayerActor())
    monster.set_child(MonsterActorState())
    monster.set_child(HuntPlayerIfHurtMe())
    monster.set_child(Equipment())
    monster.set_child(Inventory())
    monster.set_child(EffectQueue())
    monster.set_child(Attacker())
    monster.set_child(RemoveEntityOnDeath())
    monster.set_child(PrintDeathMessageOnDeath())


def set_humanoid_components(composite):
    composite.set_child(BleedWhenDamaged())
    composite.set_child(StatusFlags([StatusFlags.CAN_OPEN_DOORS,
                                     StatusFlags.IS_ALIVE, StatusFlags.HAS_HEART]))
    composite.set_child(LeaveCorpseOnDeath())


def new_ratman(gamestate):
    ratman = Composite()
    set_monster_components(ratman, gamestate)
    set_humanoid_components(ratman)

    ratman.set_child(Description("Ratman", "A Rat/Man hybrid it looks hostile."))
    ratman.set_child(EntityMessages("The ratman looks at you.", "The ratman falls dead."))
    ratman.set_child(GraphicChar(None, colors.ORANGE, icon.RATMAN))

    ratman.set_child(Health(8))
    ratman.set_child(DataPoint(DataTypes.STRENGTH, 8))
    ratman.set_child(DataPoint(DataTypes.EVASION, 16))
    ratman.set_child(DataPoint(DataTypes.HIT, 13))
    ratman.set_child(DataPoint(DataTypes.ARMOR, 4))
    ratman.set_child(DataPoint(DataTypes.AWARENESS, 5))
    ratman.set_child(MonsterThrowStoneAction(30))
    return ratman


def set_insect_components(composite):
    composite.set_child(StatusFlags([StatusFlags.CAN_OPEN_DOORS, StatusFlags.IS_ALIVE]))
    composite.set_child(DataPoint(DataTypes.INTELLIGENCE, IntelligenceLevels.ANIMAL))


def new_spider(gamestate):
    spider = Composite()
    set_monster_components(spider, gamestate)
    set_insect_components(spider)

    spider.set_child(Description("Spider", "A giant spider, its attacks are poisonous."))
    spider.set_child(EntityMessages("The spider looks at you.", "The spider stops moving."))
    spider.set_child(GraphicChar(None, colors.CHAMPAGNE_D, "s"))

    spider.set_child(Health(7))
    spider.set_child(DataPoint(DataTypes.STRENGTH, 1))
    spider.set_child(DataPoint(DataTypes.EVASION, 13))
    spider.set_child(DataPoint(DataTypes.HIT, 5))
    spider.set_child(DataPoint(DataTypes.ARMOR, 7))
    spider.set_child(DataPoint(DataTypes.AWARENESS, 5))

    spider.set_child(UnArmedHitTargetEntityEffectFactory(PoisonEntityEffectFactory(spider,
                                                                                   1, 3,
                                                                                   random.randrange(9, 18))))
    return spider


class PoisonEntityEffectFactory(object):
    def __init__(self, source_entity, damage, turn_interval, turns_to_live):
        self.source_entity = source_entity
        self.damage = damage
        self.turn_interval = turn_interval
        self.turns_to_live = turns_to_live

    def __call__(self):
        return DamageOverTimeEffect(self.source_entity, self.damage, [DamageTypes.POISON],
                                    self.turn_interval, self.turns_to_live,
                                    messenger.POISON_MESSAGE, no_stack_id="poison")


def new_cyclops(game_state):
    cyclops = Composite()
    set_monster_components(cyclops, game_state)
    set_humanoid_components(cyclops)
    cyclops.set_child(EntityMessages("The eye of the cyclops watches at you.",
                                     "The cyclops is dead."))
    cyclops.set_child(Description("Cyclops",
                                  "A Giant with a single disgusting eye, it's looking for prey."))
    cyclops.set_child(GraphicChar(None, colors.LIGHT_ORANGE, icon.CYCLOPS))
    cyclops.set_child(Health(45))
    cyclops.set_child(DataPoint(DataTypes.MOVEMENT_SPEED, gametime.single_turn))
    cyclops.set_child(DataPoint(DataTypes.THROW_SPEED, gametime.double_turn))
    cyclops.set_child(DataPoint(DataTypes.STRENGTH, 21))
    cyclops.set_child(DataPoint(DataTypes.EVASION, 5))
    cyclops.set_child(DataPoint(DataTypes.HIT, 11))
    cyclops.set_child(DataPoint(DataTypes.ARMOR, 6))
    cyclops.set_child(DataPoint(DataTypes.AWARENESS, 3))
    cyclops.set_child(DataPoint(DataTypes.MOVEMENT_SPEED, gametime.one_and_half_turn))
    cyclops.set_child(DataPoint(DataTypes.THROW_SPEED, gametime.double_turn))
    cyclops.set_child(DataPoint(DataTypes.MELEE_DAMAGE_MULTIPLIER, 0.5))

    cyclops.set_child(MonsterThrowStoneAction(10, icon=icon.DUNGEON_WALLS_ROW))
    return cyclops


def new_jericho(gamestate):
    jericho = new_ratman(gamestate)
    jericho.description.name = "Jericho"
    jericho.entity_messages.death_message = "Jericho the quick is no more."
    jericho.set_child(Flag("is_named"))
    jericho.graphic_char.color_fg = colors.YELLOW
    jericho.actor.energy_recovery = gametime.double_energy_gain
    return jericho


def set_ghost_components(composite):
    composite.set_child(StatusFlags([StatusFlags.CAN_OPEN_DOORS, StatusFlags.FLYING]))


def new_ghost(gamestate):
    ghost = Composite()
    set_monster_components(ghost, gamestate)
    set_ghost_components(ghost)

    ghost.set_child(EntityMessages("The ghost sees you.", "The ghost fades away."))
    ghost.set_child(Description("Ghost", "A spirit of a hunted creature."))
    ghost.set_child(GraphicChar(None, colors.LIGHT_BLUE, icon.GHOST))
    ghost.set_child(Health(1))
    ghost.set_child(DataPoint(DataTypes.STRENGTH, 2))
    ghost.set_child(DataPoint(DataTypes.EVASION, 22))
    ghost.set_child(DataPoint(DataTypes.HIT, 14))
    ghost.set_child(DataPoint(DataTypes.ARMOR, 0))
    ghost.set_child(DataPoint(DataTypes.MOVEMENT_SPEED, gametime.single_turn + gametime.one_third_turn))
    ghost.set_child(DataPoint(DataTypes.AWARENESS, 8))

    ghost.set_child(KeepPlayerAtDistanceActor(4))
    ghost.set_child(MonsterMagicRangeAction(1, 60))
    ghost.set_child(AddGhostReviveToSeenEntities())
    return ghost


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
            if (entity.status_flags.has_status(StatusFlags.IS_ALIVE) and
                        entity.intelligence.value >= IntelligenceLevels.NORMAL and
                    not entity.has("is_player")):
                effect = ReviveAsGhostOnDeath(self.parent)
                entity.effect_queue.add(AddSpoofChild(self.parent, effect, 1))


class ReviveAsGhostOnDeath(Leaf):
    """
    Will remove the parent from the dungeon when parent Entity dies.
    """

    def __init__(self, source_entity):
        super(ReviveAsGhostOnDeath, self).__init__()
        self.component_type = "revive_as_ghost_on_death"
        self.source_entity = source_entity

    def on_tick(self, time):
        if self.parent.health.is_dead():
            ghost = new_ghost(self.parent.game_state.value)
            ghost.mover.replace_move(self.parent.position.value, self.parent.dungeon_level.value)
            self._animate(ghost)
            self._send_revive_message()
            _skip_turn(ghost)

    def _animate(self, ghost):
        ghost.char_printer.append_default_graphic_frame()
        ghost.char_printer.append_graphic_char_temporary_frames([self.parent.graphic_char])

    def _send_revive_message(self):
        messenger.msg.send_visual_message(
            messenger.HAUNT_MESSAGE % {"source_entity": self.source_entity.description.name,
                                       "target_entity": self.parent.description.name},
            self.parent.position.value)


def _skip_turn(entity):
    immobile_stepper = ImmobileStepper()
    add_spoof_effect = AddSpoofChild(entity, immobile_stepper, gametime.single_turn)
    entity.effect_queue.add(add_spoof_effect)


def set_slime_components(slime):
    slime.set_child(StatusFlags([StatusFlags.IS_ALIVE]))
    slime.set_child(DataPoint(DataTypes.INTELLIGENCE, IntelligenceLevels.PLANT))
    slime.set_child(DataPoint(DataTypes.MOVEMENT_SPEED, gametime.single_turn + gametime.one_third_turn))
    slime.set_child(Flag("is_slime"))
    slime.remove_component_of_type("attacker")


def new_slime(game_state):
    slime = Composite()
    set_monster_components(slime, game_state)
    set_slime_components(slime)

    slime.set_child(SlimeCanShareTileEntityMover())
    slime.set_child(DissolveEntitySlimeShareTileEffect())
    slime.set_child(EntityMessages("The slime seems to wobble with happiness.", "The slime melts away."))
    slime.set_child(Description("Slime",
                                "Slime, slime, slime. Ugh, I hate Slimes." "The slime seem to sense at you..."))
    slime.set_child(GraphicChar(None, colors.GREEN, icon.SLIME))
    slime.set_child(Health(35))
    slime.set_child(DataPoint(DataTypes.STRENGTH, 2))
    slime.set_child(DataPoint(DataTypes.EVASION, 7))
    slime.set_child(DataPoint(DataTypes.HIT, 15))
    slime.set_child(DataPoint(DataTypes.ARMOR, 3))
    slime.set_child(DataPoint(DataTypes.MOVEMENT_SPEED, gametime.single_turn + gametime.one_third_turn))
    slime.set_child(DataPoint(DataTypes.AWARENESS, 5))
    return slime


def new_dark_slime(game_state):
    slime = Composite()
    set_monster_components(slime, game_state)
    set_slime_components(slime)

    slime.set_child(SlimeCanShareTileEntityMover())
    slime.set_child(DissolveEntitySlimeShareTileEffect())
    slime.set_child(BlockVisionShareTileEffect())
    slime.set_child(EntityMessages("The dark slime seems to wobble with happiness.", "The dark slime melts away."))
    slime.set_child(Description("Dark Slime",
                                "Slime, slime, slime. Ugh, I hate Slimes." "The dark slime seem to sense at you..."))
    slime.set_child(GraphicChar(None, colors.BLUE, icon.SLIME))
    slime.set_child(Health(45))
    slime.set_child(DataPoint(DataTypes.STRENGTH, 2))
    slime.set_child(DataPoint(DataTypes.EVASION, 8))
    slime.set_child(DataPoint(DataTypes.HIT, 15))
    slime.set_child(DataPoint(DataTypes.ARMOR, 3))
    slime.set_child(DataPoint(DataTypes.AWARENESS, 6))
    return slime


class EntityShareTileEffect(Leaf):
    """
    Defines an effect that sharing tile with this parent entity will result in.
    """

    def __init__(self):
        super(EntityShareTileEffect, self).__init__()
        self.tags = ["entity_share_tile_effect"]

    def share_tile_effect_tick(self, sharing_entity, time_spent):
        if not sharing_entity is self.parent:
            self._effect(source_entity=self.parent, target_entity=sharing_entity, time=time_spent)

    def _effect(self, **kwargs):
        pass


class DissolveEntitySlimeShareTileEffect(EntityShareTileEffect):
    def __init__(self):
        super(DissolveEntitySlimeShareTileEffect, self).__init__()
        self.component_type = "dissolve_entity_slime_share_tile_effect"

    def _effect(self, **kwargs):
        target_entity = kwargs["target_entity"]
        source_entity = kwargs["source_entity"]
        strength = source_entity.strength.value
        damage = rng.random_variance(strength, 1)

        if len(target_entity.get_children_with_tag("entity_share_tile_effect")) > 0:
            #Merge with other slime.
            return
            #self.parent.health_modifier.increases_max_hp(target_entity.health.hp.max_value / 2)
            #self.parent.health_modifier.heal(target_entity.health.hp.value / 2)
            #target_entity.health_modifier.kill(self.parent)
        else:
            #Damage other creature.
            dissolve_effect = UndodgeableDamagAndBlockSameEffect(source_entity, damage, [DamageTypes.ACID],
                                                                 messenger.DISSOLVE_MESSAGE,
                                                                 EffectStackID.SLIME_DISSOLVE,
                                                                 time_to_live=gametime.single_turn)
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
        if rng.stat_check(my_strength, slime_strength + 8):
            self._make_slime_skip_turn()
            return self.next.try_move_or_bump(position)
        return self.parent.movement_speed.value

    def _make_slime_skip_turn(self):
        immobile_stepper = ImmobileStepper()
        add_spoof_effect = AddSpoofChild(self.parent, immobile_stepper, gametime.single_turn)
        self._slime.effect_queue.add(add_spoof_effect)


class BlockVisionShareTileEffect(EntityShareTileEffect):
    def __init__(self):
        super(BlockVisionShareTileEffect, self).__init__()
        self.component_type = "block_vision_share_tile_effect"

    def _effect(self, **kwargs):
        target_entity = kwargs["target_entity"]
        source_entity = kwargs["source_entity"]
        sight_radius_spoof = DataPoint(DataTypes.SIGHT_RADIUS, 1)
        darkness_effect = AddSpoofChild(source_entity, sight_radius_spoof, time_to_live=1)
        target_entity.effect_queue.add(darkness_effect)
