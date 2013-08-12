from collections import deque
import turn
import entity
import gametime
import player


class RepeatCallFunctionEntity(entity.Entity):
    """
    An fake entity that will call a function instead of acting.
    """
    def __init__(self, function, turn_time):
        super(RepeatCallFunctionEntity, self).__init__(None)
        self.function = function
        self.turn_time = gametime.single_turn
        self.energy_recovery = gametime.normal_energy_gain

    def draw(self):
        """
        This entity is a fake entity, it has no graphical representation.
        """
        pass

    def act(self):
        """
        This fake entity will call a function instead of acting.
        """
        self.function()
        return self.turn_time

    def update_dungeon_map_if_its_old(self):
        """
        This entity is fake updating a map is unecessary.
        """
        pass


class EntityScheduler(object):
    def __init__(self):
        self._entities = deque()
        once_a_turn_update_caller_entity =\
            RepeatCallFunctionEntity(self._update_once_a_turn,
                                     gametime.single_turn)
        self._entities.append(once_a_turn_update_caller_entity)
        self._entities_effects_update_timer = 0

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
            self._update_entity_dungeon_map(entity)
            while entity.energy > 0:
                # The user is presented with the latest state.
                if(isinstance(entity, player.Player)):
                    entity.game_state.force_draw()
                entity.energy -= entity.act()
            turn.current_turn += 1

    def update_entities(self):
        self._entities_tick()

    def _update_once_a_turn(self):
        self._entities_equipment_effects()
        self._entities_clear_status()
        self._entities_effects_update()

    def _update_entity_dungeon_map(self, entity):
        entity.update_dungeon_map_if_its_old()
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
            entity.clear_all_temporary_status_flags()
