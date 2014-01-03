from attacker import Attacker, Dodger, ArmorChecker
import colors
from compositecore import Composite
import compositereader
from dungeonmask import DungeonMask, Path
from entityeffect import EffectQueue
from equipment import Equipment
import gametime
from graphic import CharPrinter
from health import Health, HealthModifier
import icon
from inventory import Inventory
from missileaction import MonsterThrowStoneAction
from monster import DissolveEntitySlimeShareTileEffect
from monsteractor import ChasePlayerActor, MonsterActorState, HuntPlayerIfHurtMe
from mover import CanShareTileEntityMover, Mover, Stepper
from ondeath import RemoveEntityOnDeath, PrintDeathMessageOnDeath
from position import Position, DungeonLevel
from stats import Stealth, Evasion, Strength, Hit, Awareness, Armor, GamePieceType, Faction, MovementSpeed, AttackSpeed
from statusflags import StatusFlags
from vision import AwarenessChecker, Vision


def set_color_fg(composite, color_name):
    composite.graphic_char.color_fg = getattr(colors, color_name)


def set_icon(composite, icon_name):
    composite.graphic_char.icon = getattr(icon, icon_name)


def set_game_piece_type(composite, game_piece_type_name):
    composite.set_child(getattr(GamePieceType, game_piece_type_name))


def set_faction(composite, faction_name):
    composite.set_child(getattr(Faction, faction_name))


component_statement_functions = {
    "color": set_color_fg,
    "icon": set_icon,
    "health": lambda composite, health: composite.set_child(Health(health)),
    "strength": lambda composite, strength: composite.set_child(Strength(strength)),
    "evasion": lambda composite, evasion: composite.set_child(Evasion(evasion)),
    "hit": lambda composite, hit: composite.set_child(Hit(hit)),
    "stealth": lambda composite, stealth: composite.set_child(Stealth(stealth)),
    "awareness": lambda composite, awareness: composite.set_child(Awareness(awareness)),
    "armor": lambda composite, armor: composite.set_child(Armor(armor)),
    "flags": lambda composite, flags: composite.set_child(StatusFlags(flags)),

    "attacker": lambda composite: composite.set_child(Attacker()),
    "game_piece_type": lambda composite, game_piece_type: set_game_piece_type(composite, game_piece_type),
    "position": lambda composite: composite.set_child(Position()),
    "dungeon_level": lambda composite: composite.set_child(DungeonLevel()),
    "mover": lambda composite: composite.set_child(Mover()),
    "stepper": lambda composite: composite.set_child(Stepper()),
    "char_printer": lambda composite: composite.set_child(CharPrinter()),
    "faction": lambda composite, faction: set_faction(composite, faction),
    "health_modifier": lambda composite: composite.set_child(HealthModifier()),
    "movement_speed": lambda composite, time: composite.set_child(MovementSpeed(getattr(gametime, time))),
    "attack_speed": lambda composite, time: composite.set_child(AttackSpeed(getattr(gametime, time))),
    "dodger": lambda composite: composite.set_child(Dodger()),
    "armor_checker": lambda composite: composite.set_child(ArmorChecker()),
    #"sight_radius": lambda composite, radius: composite.set_child(SightRadius(radius)),
    "awareness_checker": lambda composite: composite.set_child(AwarenessChecker()),
    "dungeon_mask": lambda composite: composite.set_child(DungeonMask()),
    "vision": lambda composite: composite.set_child(Vision()),
    "path": lambda composite: composite.set_child(Path()),
    "chase_player_actor": lambda composite: composite.set_child(ChasePlayerActor()),
    "monster_actor_state": lambda composite: composite.set_child(MonsterActorState()),
    "hunt_player_if_hurt_me": lambda composite: composite.set_child(HuntPlayerIfHurtMe()),
    "equipment": lambda composite: composite.set_child(Equipment()),
    "inventory": lambda composite: composite.set_child(Inventory()),
    "effect_queue": lambda composite: composite.set_child(EffectQueue()),
    "remove_entity_on_death": lambda composite: composite.set_child(RemoveEntityOnDeath()),
    "print_death_message_on_death": lambda composite: composite.set_child(PrintDeathMessageOnDeath()),
    #"game_state": lambda composite, health: composite.set_child(GameState(game_state)),

    "CanShareTileEntityMover": lambda composite: composite.set_child(CanShareTileEntityMover()),
    "DissolveEntitySlimeShareTileEffect": lambda composite: composite.set_child(DissolveEntitySlimeShareTileEffect()),
    "MonsterThrowStoneAction": lambda composite: composite.set_child(MonsterThrowStoneAction()),
}

composite_library = compositereader.get_library("monster.txt")


def get_monster(monster_name):
    monster_library = composite_library[monster_name]
    monster = Composite()
    for statement in monster_library.keys():
        function = component_statement_functions[statement[0]]
        arguments = [monster] + statement[1:]
        function(**arguments)
