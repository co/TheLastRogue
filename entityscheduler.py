from collections import deque
import turn
import player


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
        if len(self._entities) > 0:
            entity = self._entities[0]
            self._entities.rotate()
            entity.energy += entity.energy_recovery
            self._update_once_a_tick(entity, entity.energy_recovery)
            self._update_entity_dungeon_map(entity)
            while entity.energy > 0:
                # The user is presented with the latest state.
                if(isinstance(entity, player.Player)):
                    entity.game_state.force_draw()
                entity.energy -= entity.act()
            turn.current_turn += 1

    def update_entities(self):
        self._entities_tick()

    def _update_once_a_tick(self, entity, time_spent):
        if(not entity.is_dead()):
            entity.equipment.execute_equip_effects()
            entity.clear_all_temporary_status_flags()
            entity.update_effect_queue(time_spent)

    def _update_entity_dungeon_map(self, entity):
        entity.update_dungeon_map_if_its_old()
        self._dungeon_map_timestamp = turn.current_turn
