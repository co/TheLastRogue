from Status import POISON_STATUS_DESCRIPTION
from attacker import DamageTypes
from compositecore import Leaf
from entityeffect import DamageOverTimeEffect
import messenger


class EntityShareTileEffect(Leaf):
    """
    Defines an effect that sharing tile with this parent entity will result in.
    """

    def __init__(self):
        super(EntityShareTileEffect, self).__init__()
        self.tags.add("entity_share_tile_effect")

    def share_tile_effect_tick(self, sharing_entity, time_spent):
        if (not sharing_entity is self.parent and
                self.can_effect(source_entity=self.parent, target_entity=sharing_entity, time=time_spent)):
            self.effect(source_entity=self.parent, target_entity=sharing_entity, time=time_spent)

    def effect(self, **kwargs):
        pass

    def can_effect(self, **kwargs):
        return True


class PoisonEntityEffectFactory(object):
    def __init__(self, source_entity, total_damage, turn_interval, turns_to_live):
        self.source_entity = source_entity
        self.total_damage = total_damage
        self.turn_interval = turn_interval
        self.turns_to_live = turns_to_live

    def __call__(self):
        damage_per_turn = self.total_damage / (self.turns_to_live / self.turn_interval)
        return DamageOverTimeEffect(self.source_entity, damage_per_turn, [DamageTypes.POISON],
                                    self.turn_interval, self.turns_to_live,
                                    messenger.POISON_MESSAGE, POISON_STATUS_DESCRIPTION, no_stack_id="poison")