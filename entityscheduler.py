from collections import deque
import turn


class EntityScheduler(object):
    def __init__(self):
        self._entities = deque()

    @property
    def entities(self):
        return list(self._entities)

    def register(self, enity):
        self._entities.append(enity)
        enity.action_points = 0

    def release(self, enity):
        self._entities.remove(enity)

    def _entities_tick(self):
        self.player_has_acted = False
        if len(self._entities) > 0:
            entity = self._entities[0]
            self._entities.rotate()
            entity.energy += entity.energy_recovery
            while entity.energy > 0:
                entity.energy -= entity.act()

    def update_entities(self):
        self._entities_tick()
        self._entities_equipment_effects()
        self._entities_clear_status()
        self._entities_effects_update()

    def _entities_calculate_dungeon_map(self):
        for entity in self._entities:
            entity.update_dungeon_map()
        self._dungeon_map_timestamp = turn.current_turn

    def _entities_effects_update(self):
        for entity in self._entities:
            entity.update_effect_queue()

    def _entities_equipment_effects(self):
        for entity in self._entities:
            if(not entity.is_dead()):
                entity.equipment.execute_equip_effects()

    def _entities_clear_status(self):
        for entity in self._entities:
            entity.clear_all_status()
