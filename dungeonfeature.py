import random
from compositecore import Composite, Leaf
import entityeffect
from graphic import GraphicChar, CharPrinter
import messenger
from mover import Mover, teleport_monsters
from position import Position, DungeonLevel
from stats import GamePieceType
from text import Description
import action
import colors
import icon


class StairsDown(Composite):
    """
    Stairs Down allows the player to descend to the next level.
    """
    def __init__(self):
        super(StairsDown, self).__init__()
        self.set_child(GamePieceType(GamePieceType.DUNGEON_FEATURE))
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(Description("Stairs Down",
                                   ("A dark pass way downward.",
                                    "what horrors awaits there?")))
        self.set_child(GraphicChar(None, colors.WHITE,
                                   icon.STAIRS_DOWN))

        self.set_child(CharPrinter())
        self.set_child(DescendStairsAction())
        self.set_child(Mover())
        self.set_child(IsDungeonFeature())


class StairsUp(Composite):
    """
    Stairs up allows the player to ascend to the next level.
    """
    def __init__(self):
        super(StairsUp, self).__init__()
        self.set_child(GamePieceType(GamePieceType.DUNGEON_FEATURE))
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(Description("Stairs Up",
                                   ("A way back, when the ",
                                    "nightmare becomes too real.")))
        self.set_child(GraphicChar(None, colors.WHITE,
                                   icon.STAIRS_UP))
        self.set_child(CharPrinter())
        self.set_child(Mover())
        self.set_child(IsDungeonFeature())


class Fountain(Composite):
    """
    Drinking from the fountain makes the player stronger.
    """
    def __init__(self):
        super(Fountain, self).__init__()
        self.set_child(GamePieceType(GamePieceType.DUNGEON_FEATURE))
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(Description("Fountain",
                                   ("A Fountain full of clean water",
                                    "surely you will become more",
                                    "healthy by drinking this.")))
        self.set_child(GraphicChar(None, colors.CYAN,
                                   icon.FOUNTAIN_FULL))
        self.set_child(CharPrinter())
        self.set_child(Mover())
        self.set_child(IsDungeonFeature())
        self.set_child(DrinkFromFountainAction())


class DrinkFromFountainAction(action.Action):
    def __init__(self):
        super(DrinkFromFountainAction, self).__init__()
        self.component_type = "descend_stairs_action"
        self.name = "Drink (Fountain)"
        self.display_order = 50

    def act(self, **kwargs):
        target_entity = kwargs["target_entity"]
        heal = random.randrange(3, 7)
        target_entity.health_modifier.increases_max_hp(heal)  # Players gain 3-6 hp for drinking.
        messenger.msg.send_global_message(messenger.DRINK_FOUNTAIN_MESSAGE % {"health": heal})
        self._dry_up_fountain()
        self.add_energy_spent_to_entity(target_entity)

    def _dry_up_fountain(self):
        self.parent.graphic_char.icon = icon.FOUNTAIN_EMPTY
        self.parent.graphic_char.color_fg = colors.GRAY_D
        self.parent.remove_component(self)


class IsDungeonFeature(Leaf):
    """
    Defines that the parent is a dungeon feature.
    """
    def __init__(self):
        super(IsDungeonFeature, self).__init__()
        self.component_type = "is_dungeon_feature"


class DescendStairsAction(action.Action):
    def __init__(self):
        super(DescendStairsAction, self).__init__()
        self.component_type = "descend_stairs_action"
        self.name = "Descend (Stairs)"
        self.display_order = 50

    def act(self, **kwargs):
        target_entity = kwargs["target_entity"]
        current_depth = target_entity.dungeon_level.value.depth
        dungeon = target_entity.dungeon_level.value.dungeon
        next_dungeon_level = dungeon.get_dungeon_level(current_depth + 1)
        self.add_energy_spent_to_entity(target_entity)
        if next_dungeon_level is None:
            return
        destination_position = next_dungeon_level.up_stairs[0].position.value
        target_entity.mover.move_push_over(destination_position, next_dungeon_level)
        teleport_monsters(target_entity)
        self._go_down_rest_heal(target_entity)

    def _go_down_rest_heal(self, target_entity):
        min_heal = 5
        max_heal = 8
        heal = random.randrange(min_heal, max_heal + 1)
        heal_effect = entityeffect.Heal(target_entity, heal)
        target_entity.effect_queue.add(heal_effect)
        messenger.msg.send_global_message(messenger.DOWN_STAIRS_HEAL_MESSAGE % {"health": heal})
