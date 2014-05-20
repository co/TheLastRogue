from monsteractor import MonsterWeightedAction


class SummonEntityMonsterAction(MonsterWeightedAction):
    def __init__(self, entity_factory, max_entities, weight=100):
        super(SummonEntityMonsterAction, self).__init__(weight)
        self.component_type = "monster_summon_entity_action"
        self.entity_factory = entity_factory
        self._current_entities = []
        self.max_entities = max_entities

    def act(self, **kwargs):
        self._current_entities = [e for e in self._current_entities if not e.health.is_dead()]
        print self._current_entities
        if len(self._current_entities) >= self.max_entities:
            return
        entity = self.entity_factory(self.parent.game_state.value)
        position = self.parent.position.value
        dungeon_level = self.parent.dungeon_level.value
        if not entity.mover.try_move_roll_over(position, dungeon_level):
            del entity
        else:
            self._current_entities.append(entity)
        return self.parent.melee_speed.value * 2
