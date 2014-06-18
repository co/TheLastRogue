import random
from Status import StatusDescriptionBar
from animation import animate_flight
from attacker import Attacker, Dodger, DamageTypes, ArmorChecker, ResistanceChecker, FireImmunity, KnockBackAttacker, PoisonImmunity
from cloud import new_fire_cloud, new_dust_cloud
from compositecommon import EntityShareTileEffect, PoisonEntityEffectFactory
from compositecore import Composite, Leaf, Component
import constants
import direction
from dungeonfeature import SpiderWeb
from dungeonmask import DungeonMask, Path
from entityeffect import EffectQueue, AddSpoofChild, EffectStackID, UndodgeableDamagAndBlockSameEffect, HealthRegain
import geometry
from graphic import CharPrinter, GraphicChar
from health import Health, HealthModifier, BleedWhenDamaged
from inventory import Inventory
import messenger
from missileaction import MonsterThrowStoneAction, MonsterThrowRockAction, SpiritMissile, MonsterHealTargetEntityEffect, MonsterTripTargetEffect
from monsteractor import ChasePlayerActor, MonsterActorState, HuntPlayerIfHurtMe, KeepPlayerAtDistanceActor, MonsterWeightedStepAction
from monsterspells import SummonEntityMonsterAction
from mover import Mover, Stepper, SlimeCanShareTileEntityMover, CautiousStepper, TolerateDamage
from ondeath import PrintDeathMessageOnDeath, LeaveCorpseOnDeath, RemoveEntityOnDeath, LeaveCorpseTurnIntoEntityOnDeath
from position import Position, DungeonLevel
import rng
from stats import Flag, UnArmedHitTargetEntityEffectFactory, DataPoint, DataTypes, Factions, IntelligenceLevel, Immunities
from stats import GamePieceTypes
from statusflags import StatusFlags
from text import Description, EntityMessages
from util import entity_skip_turn, entity_skip_step
from vision import Vision, AwarenessChecker
import colors
from equipment import Equipment
import gametime
import icon


def set_monster_components(monster, game_state):
    monster.set_child(DataPoint(DataTypes.ENERGY, -gametime.single_turn))
    monster.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.ENTITY))
    monster.set_child(DataPoint(DataTypes.CRIT_CHANCE, 0.15))
    monster.set_child(DataPoint(DataTypes.MOVEMENT_SPEED, gametime.single_turn))
    monster.set_child(DataPoint(DataTypes.MELEE_SPEED, gametime.single_turn))
    monster.set_child(DataPoint(DataTypes.THROW_SPEED, gametime.single_turn))
    monster.set_child(DataPoint(DataTypes.SHOOT_SPEED, gametime.single_turn))
    monster.set_child(DataPoint(DataTypes.SIGHT_RADIUS, constants.COMMON_SIGHT_RADIUS))
    monster.set_child(DataPoint(DataTypes.FACTION, Factions.MONSTER))
    monster.set_child(DataPoint(DataTypes.GAME_STATE, game_state))
    monster.set_child(DataPoint(DataTypes.INTELLIGENCE, IntelligenceLevel.NORMAL))
    monster.set_child(DataPoint(DataTypes.SKIP_ACTION_CHANCE, IntelligenceLevel.NORMAL))

    monster.set_child(Position())
    monster.set_child(CharPrinter())
    monster.set_child(DungeonLevel())
    monster.set_child(StatusDescriptionBar())

    monster.set_child(Mover())
    monster.set_child(CautiousStepper())

    monster.set_child(HealthModifier())
    monster.set_child(Dodger())
    monster.set_child(ArmorChecker())
    monster.set_child(ResistanceChecker())
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
    monster.set_child(MonsterWeightedStepAction(100))
    monster.set_child(StatusFlags([]))


def set_humanoid_components(composite):
    composite.set_child(BleedWhenDamaged())
    composite.set_child(StatusFlags([StatusFlags.CAN_OPEN_DOORS,
                                     StatusFlags.IS_ALIVE, StatusFlags.HAS_HEART]))
    composite.set_child(LeaveCorpseOnDeath())


def set_skeleton_components(composite):
    composite.set_child(StatusFlags([StatusFlags.CAN_OPEN_DOORS]))
    composite.set_child(PoisonImmunity())
    composite.set_child(TolerateDamage(DamageTypes.POISON))


def new_ratman(gamestate):
    ratman = Composite()
    set_monster_components(ratman, gamestate)
    set_humanoid_components(ratman)

    ratman.set_child(Description("Ratman", "A Rat/Man hybrid, it looks hostile."))
    ratman.set_child(EntityMessages("The ratman looks at you.", "The ratman falls dead."))
    ratman.set_child(GraphicChar(None, colors.ORANGE, icon.RATMAN))

    ratman.set_child(Health(8))
    ratman.set_child(DataPoint(DataTypes.STRENGTH, 3))
    ratman.set_child(DataPoint(DataTypes.EVASION, 16))
    ratman.set_child(DataPoint(DataTypes.HIT, 13))
    ratman.set_child(DataPoint(DataTypes.ARMOR, 4))
    ratman.set_child(DataPoint(DataTypes.AWARENESS, 5))

    ratman.set_child(MonsterThrowStoneAction(20))

    ratman.set_child(DataPoint(DataTypes.MINIMUM_DEPTH, 1))
    return ratman


def new_ratman_mystic(gamestate):
    ratman = Composite()
    set_monster_components(ratman, gamestate)
    set_humanoid_components(ratman)

    ratman.set_child(Description("Ratman Mystic", "A Rat/Man hybrid, it looks hostile."))
    ratman.set_child(EntityMessages("The ratman looks at you.", "The ratman falls dead."))
    ratman.set_child(GraphicChar(None, colors.PURPLE, icon.RATMAN))

    ratman.set_child(Health(6))
    ratman.set_child(DataPoint(DataTypes.STRENGTH, 2))
    ratman.set_child(DataPoint(DataTypes.EVASION, 18))
    ratman.set_child(DataPoint(DataTypes.HIT, 11))
    ratman.set_child(DataPoint(DataTypes.ARMOR, 3))
    ratman.set_child(DataPoint(DataTypes.AWARENESS, 6))

    ratman.set_child(SpiritMissile(15))
    ratman.set_child(SummonEntityMonsterAction(new_worm, 5, 20))
    ratman.set_child(DataPoint(DataTypes.MOVEMENT_SPEED, gametime.single_turn + gametime.quarter_turn))

    ratman.set_child(KeepPlayerAtDistanceActor(4))

    ratman.set_child(DataPoint(DataTypes.MINIMUM_DEPTH, 3))
    return ratman


def new_worm(gamestate):
    worm = Composite()
    set_monster_components(worm, gamestate)

    worm.set_child(Description("Worm", "It's a giant earth worm."))
    worm.set_child(EntityMessages("The worm wiggles at you.", "The worm stops moving."))
    worm.set_child(GraphicChar(None, colors.PINK, "w"))

    worm.set_child(Health(4))
    worm.set_child(DataPoint(DataTypes.STRENGTH, 3))
    worm.set_child(DataPoint(DataTypes.EVASION, 12))
    worm.set_child(DataPoint(DataTypes.HIT, 10))
    worm.set_child(DataPoint(DataTypes.ARMOR, 2))
    worm.set_child(DataPoint(DataTypes.AWARENESS, 3))
    worm.set_child(DataPoint(DataTypes.MOVEMENT_SPEED, gametime.one_and_half_turn))

    return worm


def new_skeleton(gamestate):
    skeleton = Composite()
    set_monster_components(skeleton, gamestate)
    set_skeleton_components(skeleton)

    skeleton.set_child(LeaveCorpseTurnIntoEntityOnDeath(new_skeleton, 0.5))

    skeleton.set_child(Description("Skeleton", "An undead skeleton it looks hostile."))
    skeleton.set_child(EntityMessages("The skeleton turns to you.", "The skeleton falls in a pile of bones."))
    skeleton.set_child(GraphicChar(None, colors.WHITE, icon.SKELETON_WARRIOR))

    skeleton.set_child(Health(10))
    skeleton.set_child(DataPoint(DataTypes.STRENGTH, 6))
    skeleton.set_child(DataPoint(DataTypes.EVASION, 18))
    skeleton.set_child(DataPoint(DataTypes.HIT, 13))
    skeleton.set_child(DataPoint(DataTypes.ARMOR, 12))
    skeleton.set_child(DataPoint(DataTypes.AWARENESS, 4))

    skeleton.set_child(DataPoint(DataTypes.MINIMUM_DEPTH, 4))
    return skeleton


def set_beast_components(composite):
    composite.set_child(StatusFlags([StatusFlags.IS_ALIVE]))
    composite.set_child(DataPoint(DataTypes.INTELLIGENCE, IntelligenceLevel.ANIMAL))
    composite.set_child(LeaveCorpseOnDeath())
    composite.set_child(BleedWhenDamaged())


def set_insect_components(composite):
    composite.set_child(StatusFlags([StatusFlags.IS_ALIVE]))
    composite.set_child(DataPoint(DataTypes.INTELLIGENCE, IntelligenceLevel.ANIMAL))


def new_spider(gamestate):
    spider = Composite()
    set_monster_components(spider, gamestate)
    set_insect_components(spider)

    spider.set_child(Description("Spider", "A giant spider, its attacks are poisonous."))
    spider.set_child(EntityMessages("The spider looks at you.", "The spider stops moving."))
    spider.set_child(GraphicChar(None, colors.CHAMPAGNE_D, icon.SPIDER))

    spider.set_child(Health(9))
    spider.set_child(DataPoint(DataTypes.STRENGTH, 1))
    spider.set_child(DataPoint(DataTypes.EVASION, 13))
    spider.set_child(DataPoint(DataTypes.HIT, 5))
    spider.set_child(DataPoint(DataTypes.ARMOR, 7))
    spider.set_child(DataPoint(DataTypes.AWARENESS, 5))

    spider.set_child(MakeSpiderWebs())
    spider.set_child(Flag(Immunities.SPIDER_WEB))
    spider.set_child(UnArmedHitTargetEntityEffectFactory(PoisonEntityEffectFactory(spider, random.randrange(4, 8), 2,
                                                                                   20)))
    spider.set_child(DataPoint(DataTypes.MINIMUM_DEPTH, 3))
    return spider


def new_dust_demon(gamestate):
    demon = Composite()
    set_monster_components(demon, gamestate)
    set_humanoid_components(demon)

    demon.set_child(Description("Dust Demon", "The demon constantly creates dust clouds."))
    demon.set_child(EntityMessages("The dust demon notices you.", "The demon falls to the ground."))
    demon.set_child(GraphicChar(None, colors.GRAY, icon.DEMON))

    demon.set_child(Health(12))
    demon.set_child(DataPoint(DataTypes.STRENGTH, 5))
    demon.set_child(DataPoint(DataTypes.EVASION, 12))
    demon.set_child(DataPoint(DataTypes.HIT, 25))
    demon.set_child(DataPoint(DataTypes.ARMOR, 8))
    demon.set_child(DataPoint(DataTypes.AWARENESS, 4))

    demon.set_child(MakeDustClouds())
    demon.set_child(DataPoint(DataTypes.MINIMUM_DEPTH, 4))
    return demon


def new_armored_beetle(gamestate):
    beetle = Composite()
    set_insect_components(beetle)
    set_monster_components(beetle, gamestate)

    beetle.set_child(
        Description("Armored Beetle", "A giant armored beetle, it looks like it wouldn't budge for anything."))
    beetle.set_child(EntityMessages("The armored beetle notices you.", "The armored beetle is dead."))
    beetle.set_child(GraphicChar(None, colors.PURPLE, icon.BEETLE))

    beetle.set_child(Health(17))
    beetle.set_child(DataPoint(DataTypes.STRENGTH, 2))
    beetle.set_child(DataPoint(DataTypes.EVASION, 2))
    beetle.set_child(DataPoint(DataTypes.HIT, 16))
    beetle.set_child(DataPoint(DataTypes.ARMOR, 15))
    beetle.set_child(DataPoint(DataTypes.AWARENESS, 2))

    beetle.set_child(DataPoint(DataTypes.MOVEMENT_SPEED, gametime.single_turn + gametime.one_third_turn))
    beetle.set_child(DataPoint(DataTypes.MINIMUM_DEPTH, 4))

    beetle.set_child(KnockBackAttacker())

    return beetle


def set_insect_components(composite):
    composite.set_child(StatusFlags([StatusFlags.IS_ALIVE]))
    composite.set_child(DataPoint(DataTypes.INTELLIGENCE, IntelligenceLevel.ANIMAL))


def new_salamander(gamestate):
    salamander = Composite()
    set_monster_components(salamander, gamestate)
    set_beast_components(salamander)

    salamander.set_child(Description("Salamander", "A salamander, it can start small fires."))
    salamander.set_child(EntityMessages("The salamander looks at you.", "The salamander stops moving."))
    salamander.set_child(GraphicChar(None, colors.RED, icon.SALAMANDER))

    salamander.set_child(Health(20))
    salamander.set_child(DataPoint(DataTypes.STRENGTH, 3))
    salamander.set_child(DataPoint(DataTypes.EVASION, 12))
    salamander.set_child(DataPoint(DataTypes.HIT, 15))
    salamander.set_child(DataPoint(DataTypes.ARMOR, 4))
    salamander.set_child(DataPoint(DataTypes.AWARENESS, 5))

    salamander.set_child(NaturalHealthRegain())
    salamander.set_child(PutAdjacentTilesOnFire())
    salamander.set_child(FireImmunity())
    salamander.set_child(TolerateDamage(DamageTypes.FIRE))
    salamander.set_child(DataPoint(DataTypes.MINIMUM_DEPTH, 4))

    return salamander


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

    cyclops.set_child(MonsterThrowRockAction(900))
    cyclops.set_child(DataPoint(DataTypes.MINIMUM_DEPTH, 5))
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
    composite.set_child(PoisonImmunity())
    composite.set_child(TolerateDamage(DamageTypes.POISON))


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
    ghost.set_child(SpiritMissile(150))
    ghost.set_child(AddGhostReviveToSeenEntities())
    ghost.set_child(DataPoint(DataTypes.MINIMUM_DEPTH, 2))
    return ghost


def new_pixie(gamestate):
    pixie = Composite()
    set_monster_components(pixie, gamestate)
    set_humanoid_components(pixie)
    pixie.set_child(StatusFlags([StatusFlags.CAN_OPEN_DOORS, StatusFlags.FLYING,
                                 StatusFlags.IS_ALIVE, StatusFlags.HAS_HEART]))

    pixie.set_child(EntityMessages("The pixie sees you.", "The pixie falls."))
    pixie.set_child(Description("Pixie", "A small humanoid with insect wings."))
    pixie.set_child(GraphicChar(None, colors.PINK, icon.PIXIE))
    pixie.set_child(Health(10))
    pixie.set_child(DataPoint(DataTypes.STRENGTH, 2))
    pixie.set_child(DataPoint(DataTypes.EVASION, 22))
    pixie.set_child(DataPoint(DataTypes.HIT, 14))
    pixie.set_child(DataPoint(DataTypes.ARMOR, 2))
    pixie.set_child(DataPoint(DataTypes.MOVEMENT_SPEED, gametime.two_thirds_turn))
    pixie.set_child(DataPoint(DataTypes.AWARENESS, 8))

    pixie.set_child(KeepPlayerAtDistanceActor(4))
    pixie.set_child(MonsterHealTargetEntityEffect(50))
    pixie.set_child(MonsterTripTargetEffect(50))
    pixie.set_child(DataPoint(DataTypes.MINIMUM_DEPTH, 6))
    return pixie


def set_slime_components(slime):
    slime.set_child(StatusFlags([StatusFlags.IS_ALIVE]))
    slime.set_child(DataPoint(DataTypes.INTELLIGENCE, IntelligenceLevel.PLANT))
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
    slime.set_child(DataPoint(DataTypes.AWARENESS, 5))
    slime.set_child(DataPoint(DataTypes.MINIMUM_DEPTH, 3))
    slime.set_child(DataPoint(DataTypes.CLONE_FUNCTION, new_slime))
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
    slime.set_child(DataPoint(DataTypes.MINIMUM_DEPTH, 3))
    slime.set_child(DataPoint(DataTypes.CLONE_FUNCTION, new_dark_slime))
    return slime


def new_giant_amoeba(game_state):
    amoeba = Composite()
    set_monster_components(amoeba, game_state)
    amoeba.set_child(StatusFlags([StatusFlags.IS_ALIVE]))
    amoeba.set_child(DataPoint(DataTypes.INTELLIGENCE, IntelligenceLevel.PLANT))

    amoeba.set_child(EntityMessages("The amoeba seems to wobble with happiness.", "The amoeba melts away."))
    amoeba.set_child(Description("Giant Amoeba",
                                 "A giant amoeba... How is this even possible?"
                                 "The amoeba seems to wobble in your direction..."))
    amoeba.set_child(GraphicChar(None, colors.LIGHT_GREEN, "0"))
    amoeba.set_child(Health(20))
    amoeba.set_child(DataPoint(DataTypes.STRENGTH, 4))
    amoeba.set_child(DataPoint(DataTypes.EVASION, 5))
    amoeba.set_child(DataPoint(DataTypes.HIT, 15))
    amoeba.set_child(DataPoint(DataTypes.ARMOR, 4))
    amoeba.set_child(DataPoint(DataTypes.MOVEMENT_SPEED, gametime.single_turn + gametime.one_third_turn))
    amoeba.set_child(DataPoint(DataTypes.AWARENESS, 5))

    amoeba.set_child(DataPoint(DataTypes.CLONE_FUNCTION, new_giant_amoeba))
    amoeba.set_child(NaturalHealthRegain())
    amoeba.set_child(SplitAtFullHealth())
    return amoeba


class MakeDustClouds(Leaf):
    def __init__(self):
        super(MakeDustClouds, self).__init__()
        self.component_type = "make_dust_clouds"
        self.time_interval = gametime.double_turn
        self.time_to_next_attempt = self.time_interval

    def before_tick(self, time):
        self.time_to_next_attempt -= time
        if self.time_to_next_attempt > 0:
            return
        self._spawn_dust_cloud()
        self.time_to_next_attempt = self.time_interval

    def _spawn_dust_cloud(self):
        my_position = self.parent.position.value
        dungeon_level = self.parent.dungeon_level.value
        dust = new_dust_cloud(self.parent.game_state.value, 24)
        dust.mover.replace_move(my_position, dungeon_level)


class MakeSpiderWebs(Leaf):
    def __init__(self):
        super(MakeSpiderWebs, self).__init__()
        self.component_type = "make_spider_webs"
        self.web_chance_per_turn = 0.6
        self.time_interval = gametime.single_turn
        self.time_to_next_attempt = self.time_interval

    def after_tick(self, time):
        self.time_to_next_attempt -= time
        if self.time_to_next_attempt > 0:
            return
        my_position = self.parent.position.value
        chance = self.web_chance_per_turn / float(len(direction.DIRECTIONS))
        dungeon_level = self.parent.dungeon_level.value
        for d in direction.DIRECTIONS:
            point = geometry.add_2d(my_position, d)
            if (random.random() < chance and dungeon_level and
                        len(dungeon_level.get_tile_or_unknown(point).get_entities()) == 0 and
                    self.position_can_have_web(dungeon_level, point)):
                web = SpiderWeb()
                web.mover.try_move(point, dungeon_level)
        self.time_to_next_attempt = self.time_interval

    def position_can_have_web(self, dungeon_level, position):
        surrounding_tiles = [dungeon_level.get_tile_or_unknown(geometry.add_2d(position, d))
                             for d in direction.DIRECTIONS]
        surrounding_solid_terrains = len([tile for tile in surrounding_tiles
                                          if tile.get_terrain().has("is_solid")])
        surrounding_dungeon_features = len([tile for tile in surrounding_tiles
                                            if tile.get_dungeon_feature()])
        return surrounding_dungeon_features + surrounding_solid_terrains > 2


class PutAdjacentTilesOnFire(Leaf):
    def __init__(self):
        super(PutAdjacentTilesOnFire, self).__init__()
        self.component_type = "put_adjacent_tiles_on_fire"
        self.fire_chance_per_turn = 0.5
        self.time_interval = gametime.single_turn
        self.time_to_next_burn_attempt = self.time_interval

    def after_tick(self, time):
        self.time_to_next_burn_attempt -= time
        if self.time_to_next_burn_attempt > 0:
            return
        my_position = self.parent.position.value
        chance = self.fire_chance_per_turn / float(len(direction.DIRECTIONS))
        for d in direction.DIRECTIONS:
            point = geometry.add_2d(my_position, d)
            dungeon_level = self.parent.dungeon_level.value
            fire = new_fire_cloud(self.parent.game_state.value, random.randrange(6, 10))
            if (random.random() < chance and len(dungeon_level.get_tile_or_unknown(point).get_entities()) == 0 and
                    fire.mover.can_move(point, dungeon_level)):
                animate_flight(self.parent.game_state.value, [my_position, point],
                               fire.graphic_char.icon, fire.graphic_char.color_fg)
                fire.mover.try_move(point, dungeon_level)
        self.time_to_next_burn_attempt = self.time_interval


class NaturalHealthRegain(Leaf):
    def __init__(self):
        super(NaturalHealthRegain, self).__init__()
        self.component_type = "natural_health_regain"

    def before_tick(self, time):
        health_regain = HealthRegain(self.parent, 3, 4, float("inf"), no_stack_id="natural_health_regain")
        self.parent.effect_queue.add(health_regain)
        self.parent.remove_component(self)


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
                        entity.intelligence.value >= IntelligenceLevel.NORMAL and
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
            entity_skip_step(ghost, ghost)

    def _animate(self, ghost):
        ghost.char_printer.append_default_graphic_frame()
        ghost.char_printer.append_graphic_char_temporary_frames([self.parent.graphic_char])

    def _send_revive_message(self):
        messenger.msg.send_visual_message(
            messenger.HAUNT_MESSAGE % {"source_entity": self.source_entity.description.name,
                                       "target_entity": self.parent.description.name},
            self.parent.position.value)


class AddEffectToOtherSeenEntities(Leaf):
    """
    Adds effects to seen entities other than self.
    """

    def __init__(self, effect_factory, ttl=1):
        super(AddEffectToOtherSeenEntities, self).__init__()
        self.component_type = "add_effect_to_other_seen_entities_" + str(effect_factory)
        self.effect_factory = effect_factory
        self.ttl = ttl

    def before_tick(self, time):
        seen_entities = self.parent.vision.get_seen_entities()
        for entity in seen_entities:
            if not entity is self.parent:
                entity.effect_queue.add(AddSpoofChild(self.parent, self.effect_factory(), self.ttl))


class HealAnEntityOnDeath(Leaf):
    """
    Will Heal an entity when parent has died.
    """

    def __init__(self, source_entity):
        super(HealAnEntityOnDeath, self).__init__()
        self.component_type = "heal_entity_on_death"
        self.source_entity = source_entity
        self.target_entity = source_entity

    def on_tick(self, time):
        if self.parent.health.is_dead():
            self.target_entity.health_modifier.heal(1)


class SplitAtFullHealth(Component):
    def __init__(self):
        super(SplitAtFullHealth, self).__init__()
        self.component_type = "split_at_full_health"

    def after_tick(self, time):
        if self.parent.health.hp.is_full():
            new_entity = self.parent.clone_function.value(self.parent.game_state.value)
            if new_entity.mover.try_move_roll_over(self.parent.position.value, self.parent.dungeon_level.value):
                self.parent.health.hp.decrease(self.parent.health.hp.max_value / 2)
                new_entity.health.hp.decrease(self.parent.health.hp.max_value / 2)


class DissolveEntitySlimeShareTileEffect(EntityShareTileEffect):
    def __init__(self):
        super(DissolveEntitySlimeShareTileEffect, self).__init__()
        self.component_type = "dissolve_entity_slime_share_tile_effect"

    def effect(self, **kwargs):
        target_entity = kwargs["target_entity"]
        source_entity = kwargs["source_entity"]
        strength = source_entity.strength.value
        damage = rng.random_variance(strength, 1)
        if not target_entity.has("effect_queue"):
            return

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
            self._split_slime(geometry.sub_2d(self._slime.position.value, position))
            entity_skip_turn(self.parent, self._slime)
            entity_skip_step(self.parent, self._slime)
            return self.next.try_move_or_bump(position)
        return self.parent.movement_speed.value

    def _split_slime(self, split_direction):
        if self._slime.health.hp.value < 3:
            return
        new_slime = self._slime.clone_function.value(self._slime.game_state.value)
        if new_slime.mover.try_move_roll_over(geometry.add_2d(self._slime.position.value, split_direction),
                                              self._slime.dungeon_level.value):
            health = self._slime.health.hp.value / 2
            self._slime.health.hp.value = health
            new_slime.health.hp.value = health
            new_slime.monster_actor_state.value = MonsterActorState.HUNTING


class BlockVisionShareTileEffect(EntityShareTileEffect):
    def __init__(self):
        super(BlockVisionShareTileEffect, self).__init__()
        self.component_type = "block_vision_share_tile_effect"

    def effect(self, **kwargs):
        target_entity = kwargs["target_entity"]
        source_entity = kwargs["source_entity"]
        if target_entity.has("effect_queue"):
            sight_radius_spoof = DataPoint(DataTypes.SIGHT_RADIUS, 1)
            darkness_effect = AddSpoofChild(source_entity, sight_radius_spoof, time_to_live=1)
            target_entity.effect_queue.add(darkness_effect)
