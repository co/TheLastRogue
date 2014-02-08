import unittest
from compositecore import Composite, Leaf


class TestComponent(Leaf):
    """
    Component which only has a component type. Composites with this component has this flag.
    """
    def __init__(self, component_type, tags):
        super(TestComponent, self).__init__()
        self.component_type = component_type
        self.tags = tags

tag_1 = "1"
tag_2 = "2"
tag_3 = "3"

id_1 = "A"
id_2 = "B"
id_3 = "C"
id_4 = "D"


class TestComposition(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_children_with_tag_returns_all_children_with_tag(self):
        c = Composite()
        component_1 = TestComponent(id_1, [tag_1])
        component_2 = TestComponent(id_2, [tag_1])
        c.set_child(component_1)
        c.set_child(component_2)
        self.assertIn(component_1, c.get_children_with_tag(tag_1))
        self.assertIn(component_2, c.get_children_with_tag(tag_1))

    def test_get_children_with_does_not_return_removed_children(self):
        c = Composite()
        component_1 = TestComponent(id_1, [tag_1])
        component_2 = TestComponent(id_2, [tag_1])
        c.set_child(component_1)
        c.set_child(component_2)
        c.remove_component(component_1)
        self.assertNotIn(component_1, c.get_children_with_tag(tag_1))
        self.assertIn(component_2, c.get_children_with_tag(tag_1))

    def test_get_children_with_tag_may_return_spoofed_children_with_tag(self):
        c = Composite()
        component_1 = TestComponent(id_1, [tag_1])
        component_2 = TestComponent(id_2, [tag_1])
        c.set_child(component_1)
        c.add_spoof_child(component_2)
        self.assertIn(component_1, c.get_children_with_tag(tag_1))
        self.assertIn(component_2, c.get_children_with_tag(tag_1))

    def test_get_children_with_tag_should_not_return_removed_spoofed_children(self):
        c = Composite()
        component_1 = TestComponent(id_1, [tag_1])
        component_2 = TestComponent(id_2, [tag_1])
        c.set_child(component_1)
        c.add_spoof_child(component_2)
        c.reset_spoofed_children()
        self.assertIn(component_1, c.get_children_with_tag(tag_1))
        self.assertNotIn(component_2, c.get_children_with_tag(tag_1))
