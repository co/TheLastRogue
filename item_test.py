import unittest

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
            scroll.read_action.action_trigger.act(source_entity=dummy_actor, target_entity=dummy_actor)
            self.assertTrue(dummy_actor.inventory.is_empty())
            self.assertGreater(dummy_actor.actor.newly_spent_energy, old_energy)

    def test_scroll_item_should_have_drop_action(self):
        scrolls = map(lambda f: f(None), item.scroll_factories)
        dummy_actor = get_dummy_player()
        for scroll in scrolls:
            dummy_actor.inventory.try_add(scroll)
            self.assertFalse(dummy_actor.inventory.is_empty())
            scroll.drop_action.action_trigger.act(source_entity=dummy_actor, target_entity=dummy_actor)
            self.assertTrue(dummy_actor.inventory.is_empty())
            scroll.mover.try_remove_from_dungeon()

    def test_scroll_item_should_have_drop_action(self):
        scrolls = map(lambda f: f(None), item.scroll_factories)
        for scroll in scrolls:
            dummy_actor = get_dummy_player()
            dummy_actor.inventory.try_add(scroll)
            self.assertFalse(dummy_actor.inventory.is_empty())
            scroll.drop_action.action_trigger.act(source_entity=dummy_actor, target_entity=dummy_actor)
            self.assertTrue(dummy_actor.inventory.is_empty())
            scroll.mover.try_remove_from_dungeon()

    def test_triggering_an_actiontrigger_should_trigger_all_triggereffect_siblings(self):
        flash_effect = item.FlashItemEffect()
        flash_effect.trigger = mock.MagicMock()
        remove_effect = item.RemoveItemEffect()
        remove_effect.trigger = mock.MagicMock()
        add_energy_spent_effect = item.AddEnergySpentEffect()
        add_energy_spent_effect.trigger = mock.MagicMock()

        read_effect = Composite("read_action")
        read_effect.set_child(item.ActionTrigger("Read", 90, item.READ_ACTION_TAG))
        read_effect.set_child(flash_effect)
        read_effect.set_child(remove_effect)
        read_effect.set_child(add_energy_spent_effect)

        self.assertTrue(read_effect.action_trigger.can_act())
        read_effect.action_trigger.act()

        flash_effect.trigger.assert_any_call()
        remove_effect.trigger.assert_any_call()
        add_energy_spent_effect.trigger.assert_any_call()
