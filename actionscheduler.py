from collections import deque
import turn
import player
import entity


class ActionScheduler(object):
    def __init__(self):
        self._actors = deque()

    @property
    def entities(self):
        return [actor for actor in self._actors
                if isinstance(actor, entity.Entity)]

    def register(self, enity):
        self._actors.append(enity)
        enity.action_points = 0

    def release(self, enity):
        self._actors.remove(enity)

    def _actors_tick(self):
        if len(self._actors) > 0:
            actor = self._actors[0]
            self._actors.rotate()
            actor.energy += actor.energy_recovery
            self._update_once_a_tick(actor, actor.energy_recovery)
            self._update_actor(actor)
            while actor.energy > 0:
                # The user is presented with the latest state.
                if(isinstance(actor, player.Player)):
                    actor.game_state.force_draw()
                actor.energy -= actor.act()
            turn.current_turn += 1

    def tick(self):
        self._actors_tick()

    def _update_once_a_tick(self, actor, time_spent):
        if(not actor.is_dead()):
            actor.equipment.execute_equip_effects()
            actor.clear_all_temporary_status_flags()
            actor.update_effect_queue(time_spent)

    def _update_actor(self, actor):
        actor.update_dungeon_map_if_its_old()
        self._dungeon_map_timestamp = turn.current_turn
