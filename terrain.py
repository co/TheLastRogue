import random
import animation
from attacker import DamageTypes
from compositecommon import EntityShareTileEffect
from compositecore import Leaf, Composite
import entityeffect
from graphic import GraphicChar, CharPrinter, GraphicCharTerrainCorners
from menufactory import start_accept_reject_prompt
import messenger
from mover import Mover
from position import Position, DungeonLevel
from stats import Flag, DataPoint, DataTypes, GamePieceTypes
from statusflags import StatusFlags
import colors
import icon


class TerrainFactory(object):
    def __init__(self):
        self.wall = None
        self.floor = None

    def get_wall(self):
        if self.wall is None:
            self.wall = Wall()
        return self.wall

    def get_floor(self):
        if self.floor is None:
            self.floor = Floor()
        return self.floor


terrain_factory = TerrainFactory()


class BumpAction(Leaf):
    """
    Defines what happens if the player bumps into this terrain.
    """
    def __init__(self):
        super(BumpAction, self).__init__()
        self.component_type = "bump_action"

    def bump(self, source_entity):
        pass

    def can_bump(self, source_entity):
        return True


class Floor(Composite):
    def __init__(self):
        super(Floor, self).__init__()
        self.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.TERRAIN))
        self.set_child(Mover())
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(GraphicChar(colors.FLOOR_BG,
                                   colors.FLOOR_FG,
                                   icon.CENTER_DOT))
        self.set_child(CharPrinter())
        self.set_child(Flag("is_transparent"))


class Water(Composite):
    def __init__(self):
        super(Water, self).__init__()
        self.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.TERRAIN))
        self.set_child(Mover())
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(GraphicChar(colors.BLUE_D,
                                   colors.BLUE,
                                   icon.WATER))
        self.set_child(CharPrinter())
        self.set_child(Flag("is_transparent"))


class GlassWall(Composite):
    def __init__(self):
        super(GlassWall, self).__init__()
        self.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.TERRAIN))
        self.set_child(Mover())
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(GraphicChar(colors.FLOOR_BG, colors.WHITE, icon.GLASS_WALL))
        self.set_child(CharPrinter())
        self.set_child(Flag("is_solid"))
        self.set_child(Flag("is_transparent"))


class Chasm(Composite):
    def __init__(self):
        super(Chasm, self).__init__()
        self.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.TERRAIN))
        self.set_child(Mover())
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(GraphicChar(colors.BLACK, colors.DARKNESS, icon.CHASM2))
        self.set_child(CharPrinter())
        self.set_child(Flag("is_chasm"))
        self.set_child(Flag("is_transparent"))

        self.set_child(PlayerFallDownChasmAction())
        self.set_child(PromptPlayerChasm())


class PromptPlayer(Leaf):
    def __init__(self, message):
        super(PromptPlayer, self).__init__()
        self.tags = ["prompt_player"]
        self.text = message

    def prompt_player(self, **kwargs):
        target_entity = kwargs["target_entity"]
        return start_accept_reject_prompt(target_entity.game_state.value.menu_prompt_stack,
                                          target_entity.game_state.value, self.text)


class PromptPlayerChasm(PromptPlayer):
    def __init__(self):
        super(PromptPlayerChasm, self).__init__(messenger.WANT_TO_JUMP_DOWN_CHASM)
        self.component_type = "prompt_player_chasm"


class PlayerFallDownChasmAction(EntityShareTileEffect):
    def __init__(self):
        super(PlayerFallDownChasmAction, self).__init__()
        self.component_type = "player_fall_down_chasm_share_tile_effect"

    def _effect(self, **kwargs):
        target_entity = kwargs["target_entity"]
        if target_entity.has("is_player"):
            self._animate_fall(target_entity)
            current_depth = target_entity.dungeon_level.value.depth
            dungeon = target_entity.dungeon_level.value.dungeon
            next_dungeon_level = dungeon.get_dungeon_level(current_depth + 1)
            target_position = next_dungeon_level.get_random_walkable_position_in_dungeon(target_entity)
            target_entity.mover.move_push_over(target_position, next_dungeon_level)
            self._fall_damage(target_entity)

    def _animate_fall(self, target_entity):
        color_fg = target_entity.graphic_char.color_fg
        target_entity.game_state.value.force_draw()
        graphic_chars = [target_entity.graphic_char,
                         GraphicChar(None, color_fg, icon.BIG_CENTER_DOT),
                         GraphicChar(None, color_fg, "*"),
                         GraphicChar(None, color_fg, "+"),
                         GraphicChar(None, color_fg, icon.CENTER_DOT)]
        animation.animate_point(target_entity.game_state.value, target_entity.position.value, graphic_chars)

    def _fall_damage(self, target_entity):
        min_damage = 2
        max_damage = 5
        damage = random.randrange(min_damage, max_damage + 1)
        damage_effect = entityeffect.UndodgeableAttackEntityEffect(None, damage,
                                                                   [DamageTypes.FALL], messenger.FALL_DOWN_MESSAGE)
        target_entity.effect_queue.add(damage_effect)


class Unknown(Composite):
    def __init__(self):
        super(Unknown, self).__init__()
        self.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.TERRAIN))
        self.set_child(Mover())
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(CharPrinter())
        self.set_child(GraphicChar(colors.BLACK,
                                   colors.BLACK,
                                   ' '))
        self.set_child(Flag("is_solid"))
        self.set_child(Flag("is_transparent"))


class Wall (Composite):
    def __init__(self):
        super(Wall, self).__init__()
        self.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.TERRAIN))
        self.set_child(Mover())
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(CharPrinter())
        self.set_child(GraphicCharTerrainCorners(colors.FLOOR_BG,
                                                 colors.WALL_FG,
                                                 icon.DUNGEON_WALLS_ROW,
                                                 [Wall, Door, Chasm]))
        self.set_child(Flag("is_solid"))


class Door(Composite):
    def __init__(self):
        super(Door, self).__init__()
        self.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.TERRAIN))
        self.set_child(Mover())
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(CharPrinter())
        self.set_child(GraphicChar(colors.FLOOR_BG,
                                   colors.ORANGE_D,
                                   icon.DOOR))
        self.set_child(Flag("is_solid"))

        self.set_child(OpenDoorAction())
        self.set_child(OpenDoorBumpAction())
        self.set_child(Flag("is_door"))


class OpenDoorAction(Leaf):
    """Opens the door terrain."""
    def __init__(self):
        super(OpenDoorAction, self).__init__()
        self.component_type = "open_door_action"

    def open_door(self):
        if self.parent.has("is_solid"):
            self.parent.remove_component_of_type("is_solid")
        self.parent.set_child(Flag("is_transparent"))
        self.parent.graphic_char.icon = icon.DOOR_OPEN
        self.parent.dungeon_level.value.signal_terrain_changed()


class OpenDoorBumpAction(BumpAction):
    """
    Defines what happens if the player bumps into this terrain.
    """
    def __init__(self):
        super(OpenDoorBumpAction, self).__init__()
        self.component_type = "bump_action"

    def bump(self, source_entity):
        self.parent.open_door_action.open_door()

    def can_bump(self, source_entity):
        return (self.parent.has("is_solid") and
                (source_entity.status_flags.
                 has_status(StatusFlags.CAN_OPEN_DOORS)))
