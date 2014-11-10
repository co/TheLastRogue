from compositecore import Leaf

__author__ = 'co'

STEP_NEXT_TO_ENEMY_TRIGGER_TAG = "step_next_to_enemy_trigger"
ENEMY_STEPPING_NEXT_TO_ME_TRIGGER_TAG = "enemy_stepping_next_to_me_trigger"
ON_ATTACKED_TRIGGER_TAG = "on_attacked_trigger"


class Trigger(Leaf):
    def __init__(self, extra_tags=[]):
        super(Trigger, self).__init__()
        self.component_type = "trigger"
        self.tags |= set(extra_tags)

    def trigger(self, **kwargs):
        for c in self.parent.get_children_with_tag("triggered_effect"):
            if c.can_trigger(**kwargs):
                c.trigger(**kwargs)

    def can_trigger(self, **kwargs):
        return all(c.can_trigger(**kwargs) for c in self.parent.get_children_with_tag("triggered_effect"))