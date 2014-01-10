from compositecore import Leaf


class EntityShareTileEffect(Leaf):
    """
    Defines an effect that sharing tile with this parent entity will result in.
    """

    def __init__(self):
        super(EntityShareTileEffect, self).__init__()
        self.tags.add("entity_share_tile_effect")

    def share_tile_effect_tick(self, sharing_entity, time_spent):
        if not sharing_entity is self.parent:
            self._effect(source_entity=self.parent, target_entity=sharing_entity, time=time_spent)

    def _effect(self, **kwargs):
        pass

