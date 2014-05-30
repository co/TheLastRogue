import random
from compositecommon import EntityShareTileEffect
from compositecore import Composite, Leaf
import direction
import entityeffect
import gametime
import geometry
from graphic import GraphicChar, CharPrinter
import menu
import menufactory
import messenger
from mover import Mover, teleport_monsters, Stepper
from position import Position, DungeonLevel
import rng
import sacrifice
import state
from stats import DataPoint, DataTypes, GamePieceTypes, Immunities
import terrain
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
        self.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.DUNGEON_FEATURE))
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
        self.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.DUNGEON_FEATURE))
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


class SpiderWeb(Composite):
    """
    Spider web the player or other entities can get caught in.
    """
    def __init__(self):
        super(SpiderWeb, self).__init__()
        self.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.DUNGEON_FEATURE))
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(Description("Spider Web",
                                   "A spider made this web, touch it and you might get stuck"))
        self.set_child(GraphicChar(None, colors.WHITE, "#"))

        self.set_child(CharPrinter())
        self.set_child(Mover())
        self.set_child(DataPoint(DataTypes.STRENGTH, 10))
        self.set_child(IsDungeonFeature())
        self.set_child(StuckInSpiderWebShareTileEffect())


class StuckInSpiderWebShareTileEffect(EntityShareTileEffect):
    def __init__(self):
        super(StuckInSpiderWebShareTileEffect, self).__init__()
        self.component_type = "stuck_in_spider_web_share_tile_effect"

    def effect(self, **kwargs):
        target_entity = kwargs["target_entity"]
        source_entity = kwargs["source_entity"]

        if not target_entity.has(Immunities.SPIDER_WEB) and target_entity.has("effect_queue"):
            stuck_in_web = StuckInWebStepperSpoof(self.parent)
            add_spoof_effect = entityeffect.AddSpoofChild(source_entity, stuck_in_web, time_to_live=1)
            target_entity.effect_queue.add(add_spoof_effect)


class StuckInWebStepperSpoof(Stepper):
    def __init__(self, web):
        super(StuckInWebStepperSpoof, self).__init__()
        self.component_type = "stepper"
        self.web = web
        self.strength = web.strength.value

    def try_move_or_bump(self, position):
        my_strength = self.parent.strength.value
        if rng.stat_check(my_strength, self.strength):
            messenger.msg.send_visual_message(messenger.BREAKS_OUT_OF_WEB_MESSAGE % {"target_entity": self.parent.description.long_name}, self.parent.position.value)
            self.web.mover.try_remove_from_dungeon()
            return self.next.try_move_or_bump(position)
        messenger.msg.send_visual_message(messenger.WONT_BREAK_OUT_OF_WEB_MESSAGE % {"target_entity": self.parent.description.long_name}, self.parent.position.value)
        return self.parent.movement_speed.value


class Fountain(Composite):
    """
    Drinking from the fountain makes the player stronger.
    """
    def __init__(self):
        super(Fountain, self).__init__()
        self.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.DUNGEON_FEATURE))
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
        self.component_type = "drink_action"
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


class BloodFountain(Composite):
    """
    Drinking from the fountain makes the player stronger.
    """
    def __init__(self):
        super(BloodFountain, self).__init__()
        self.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.DUNGEON_FEATURE))
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(Description("Fountain Of Sacrifice",
                                   ("The fountain is filled thick red liquid.",
                                    "You have a feeling that it calls out for you.")))
        self.set_child(GraphicChar(None, colors.RED, icon.FOUNTAIN_FULL))
        self.set_child(CharPrinter())
        self.set_child(Mover())
        self.set_child(IsDungeonFeature())
        self.set_child(SacrificeFountainAction())


class SacrificeFountainAction(DrinkFromFountainAction):
    def __init__(self):
        super(SacrificeFountainAction, self).__init__()
        self.component_type = "sacrifice_fountain_action"
        self.name = "Drink (Fountain)"
        self.display_order = 50

    def act(self, **kwargs):
        target_entity = kwargs["target_entity"]
        self.start_sacrifice_menu(target_entity)

    def start_sacrifice_menu(self, entity):
        menu = menufactory.sacrifice_menu(entity, entity.game_state.value.power_list, self._dry_up_fountain)
        entity.game_state.value.start_prompt(state.UIState(menu))


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
        self.component_type = "drink_action"
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
