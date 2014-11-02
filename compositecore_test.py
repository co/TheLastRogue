from pygame.tests.test_utils import unittest

from compositecore import Composite, Leaf


class DummyComponent(Leaf):
    def __init__(self, component_type, tags=[]):
        super(DummyComponent, self).__init__()
        self.component_type = component_type
        self.tags = set(tags)


class TestComposition(unittest.TestCase):

    def test_when_adding_component_of_existing_type_old_component_should_be_removed(self):
        c = Composite()
        component_first = DummyComponent("x")
        component_second = DummyComponent("x")
        c.set_child(component_first)
        c.set_child(component_second)
        self.assertFalse(c.x is component_first)
        self.assertTrue(c.x is component_second)

    def test_when_composite_should_be_able_to_get_children_of_tag(self):
        c = Composite()
        component1 = DummyComponent("x", "a")
        component2 = DummyComponent("y", "a")
        component3 = DummyComponent("z", "a")
        component4 = DummyComponent("Q", "Q")
        c.set_child(component1)
        c.set_child(component2)
        c.set_child(component3)
        c.set_child(component4)
        self.assertFalse(component4 in c.get_children_with_tag("a"))
        self.assertTrue(component1 in c.get_children_with_tag("a"))
        self.assertTrue(component2 in c.get_children_with_tag("a"))
        self.assertTrue(component3 in c.get_children_with_tag("a"))

    def test_when_a_component_is_removed_it_should_not_be_gettable_by_tag(self):
        c = Composite()
        component1 = DummyComponent("x", "a")
        c.set_child(component1)
        self.assertEqual(len(c.get_children_with_tag("a")), 1)
        self.assertTrue(component1 in c.get_children_with_tag("a"))
        c.remove_component(component1)
        self.assertEqual(len(c.get_children_with_tag("a")), 0)
        self.assertFalse(component1 in c.get_children_with_tag("a"))

    def test_when_a_component_is_removed_by_type_it_should_not_be_gettable_by_tag(self):
        c = Composite()
        component1 = DummyComponent("x", "a")
        c.set_child(component1)
        self.assertEqual(len(c.get_children_with_tag("a")), 1)
        self.assertTrue(component1 in c.get_children_with_tag("a"))
        c.remove_component_of_type("x")
        self.assertEqual(len(c.get_children_with_tag("a")), 0)
        self.assertFalse(component1 in c.get_children_with_tag("a"))

    def test_when_a_component_is_overwritten_it_should_not_be_gettable_by_tag(self):
        c = Composite()
        component1 = DummyComponent("x", "a")
        component2 = DummyComponent("x", "a")
        component3 = DummyComponent("x", "a")
        c.set_child(component1)
        c.set_child(component2)
        c.set_child(component3)
        self.assertEqual(len(c.get_children_with_tag("a")), 1)
        self.assertFalse(component1 in c.get_children_with_tag("a"))
        self.assertFalse(component2 in c.get_children_with_tag("a"))
        self.assertTrue(component3 in c.get_children_with_tag("a"))

    def test_get_relative_of_type_should_return_uncle_if_uncle_matches(self):
        parent = Composite()
        grandparent = Composite()
        uncle = Composite("C")
        component1 = DummyComponent("A")
        component2 = DummyComponent("B")
        grandparent.set_child(parent)
        grandparent.set_child(uncle)
        parent.set_child(component1)
        parent.set_child(component2)
        self.assertTrue(component1.has_relative_of_type("C"),
                        "No relative with component " + component1.component_type + " was found.")
        self.assertTrue(component1.get_relative_of_type("C") is uncle)

    def test_get_relative_of_type_should_return_sibling_if_both_uncle_and_sibling_matches(self):
        parent = Composite("X")
        grandparent = Composite("Y")
        uncle = Composite("C")
        component1 = DummyComponent("Z")
        component2 = DummyComponent("W")
        component3 = DummyComponent("C")
        grandparent.set_child(parent)
        grandparent.set_child(uncle)
        parent.set_child(component1)
        parent.set_child(component2)
        parent.set_child(component3)
        self.assertTrue(component1.has_relative_of_type("C"),
                        "No relative with component " + component1.component_type + " was found.")
        self.assertTrue(component1.get_relative_of_type("C") is component3)

    def test_get_relative_of_type_should_return_sibling_if_sibling_matches(self):
        c = Composite()
        component1 = DummyComponent("A")
        component2 = DummyComponent("B")
        c.set_child(component1)
        c.set_child(component2)
        self.assertTrue(component1.has_relative_of_type("B"),
                        "No relative with component " + component1.component_type + " was found.")
        self.assertTrue(component1.get_relative_of_type("B") is component2)
