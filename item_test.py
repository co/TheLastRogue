import unittest
from action import TriggerAction

from common_test import get_dummy_player
import mock
from compositecore import Composite
import item


class TestComposition(unittest.TestCase):
    def setUp(self):
        pass

    def test_scroll_item_should_have_read_action(self):
        scroll = item.new_sleep_scroll(None)
        self.assertTrue(any(scroll.get_children_with_tag(item.READ_ACTION_TAG)), "The actor has no read action.")
        self.assertTrue(any(scroll.get_children_with_tag("user_action")), "The actor has no user action.")
        self.assertTrue(scroll.get_children_with_tag("user_action")[0].can_act(), "The actor has no user action.")

    def test_scroll_items_should_have_read_action(self):
        scrolls = map(lambda f: f(None), item.scroll_factories)
        dummy_actor = get_dummy_player()
        for scroll in scrolls:
            dummy_actor.inventory.try_add(scroll)
            old_energy = dummy_actor.actor.newly_spent_energy
            self.assertFalse(dummy_actor.inventory.is_empty())
            scroll.read_action.trigger.act(source_entity=dummy_actor, target_entity=dummy_actor)
            self.assertTrue(dummy_actor.inventory.is_empty())
            self.assertGreater(dummy_actor.actor.newly_spent_energy, old_energy)

    def test_scroll_item_should_have_drop_action(self):
        scrolls = map(lambda f: f(None), item.scroll_factories)
        dummy_actor = get_dummy_player()
        for scroll in scrolls:
            dummy_actor.inventory.try_add(scroll)
            self.assertFalse(dummy_actor.inventory.is_empty())
            scroll.drop_action.trigger.act(source_entity=dummy_actor)
            self.assertTrue(dummy_actor.inventory.is_empty())
            scroll.mover.try_remove_from_dungeon()

    def test_items_should_have_drop_action(self):
        scrolls = map(lambda f: f(None), item.scroll_factories)
        potions = map(lambda f: f(None), item.potion_factories)
        for e in scrolls + potions:
            dummy_actor = get_dummy_player()
            dummy_actor.inventory.try_add(e)
            self.assertFalse(dummy_actor.inventory.is_empty())
            e.drop_action.trigger.act(source_entity=dummy_actor, target_entity=dummy_actor)
            self.assertTrue(dummy_actor.inventory.is_empty())
            e.mover.try_remove_from_dungeon()

    def test_items_should_have_hit_ground_triggers_action(self):
        scrolls = map(lambda f: f(None), item.scroll_factories)
        potions = map(lambda f: f(None), item.potion_factories)
        for e in scrolls + potions:
            dummy_actor = get_dummy_player()
            dummy_actor.inventory.try_add(e)
            e.hit_floor_action_tag.trigger.act(target_position=(1, 3), source_entity=dummy_actor,
                                               game_state=None)
            e.hit_chasm_action_tag.trigger.act(target_position=(1, 3))
            e.mover.try_remove_from_dungeon()

    def test_potion_items_should_have_drink_action(self):
        potions = map(lambda f: f(None), item.potion_factories)
        dummy_actor = get_dummy_player()
        for potion in potions:
            dummy_actor.inventory.try_add(potion)
            old_energy = dummy_actor.actor.newly_spent_energy
            self.assertFalse(dummy_actor.inventory.is_empty())
            potion.drink_action.trigger.act(source_entity=dummy_actor, target_entity=dummy_actor,
                                            game_state=None, target_position=dummy_actor.position.value)
            self.assertTrue(dummy_actor.inventory.is_empty())
            self.assertGreater(dummy_actor.actor.newly_spent_energy, old_energy)

    def test_triggering_an_actiontrigger_should_trigger_all_triggereffect_siblings(self):
        flash_effect = item.FlashItemEffect()
        flash_effect.trigger = mock.MagicMock()
        remove_effect = item.RemoveItemEffect()
        remove_effect.trigger = mock.MagicMock()
        add_energy_spent_effect = item.AddEnergySpentEffect()
        add_energy_spent_effect.trigger = mock.MagicMock()

        read_effect = Composite("read_action")
        read_effect.set_child(TriggerAction("Read", 90, item.READ_ACTION_TAG))
        read_effect.set_child(flash_effect)
        read_effect.set_child(remove_effect)
        read_effect.set_child(add_energy_spent_effect)

        self.assertTrue(read_effect.trigger.can_act())
        read_effect.trigger.act()

        flash_effect.trigger.assert_any_call()
        remove_effect.trigger.assert_any_call()
        add_energy_spent_effect.trigger.assert_any_call()
