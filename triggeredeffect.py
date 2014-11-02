from compositecore import Leaf

__author__ = 'co'


class TriggeredEffect(Leaf):
    def __init__(self, component_type):
        super(TriggeredEffect, self).__init__()
        self.component_type = component_type
        self.tags.add("triggered_effect")

    def trigger(self, **kwargs):
        pass

    def can_trigger(self, **kwargs):
        return True