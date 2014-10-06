from collections import deque
import gametime


class ActionScheduler(object):
    def __init__(self):
        self._actors = deque()

    @property
    def entities(self):  # All monsters have health
        return [actor for actor in self._actors if actor.has("health")]

    @property
    def actors(self):
        return list(self._actors)

    def register(self, actor):
        self._actors.append(actor)

    def release(self, actor):
        self._actors.remove(actor)

    def effects_tick(self, entity):
        if entity.has("effect_queue"):
            entity.effect_queue.update(gametime.normal_energy_gain)

    def _actors_tick(self):
        if len(self._actors) > 0:
            entity = self._actors[0]
            entity.first_tick(gametime.normal_energy_gain)  # Equipped effects.
            self.effects_tick(entity)
            entity.before_tick(gametime.normal_energy_gain)
            self.on_tick(entity)
            if entity.dungeon_level.value is None or entity.position.value is None:
                return
            entity.actor.tick()
            entity.on_tick(gametime.normal_energy_gain)
            entity.after_tick(gametime.normal_energy_gain)
            self._actors.rotate()

    def on_tick(self, entity):
        self.sharing_tile_effects_tick(entity)

    def sharing_tile_effects_tick(self, actor):
        if(actor.has("dungeon_level") and
           actor.has("position")):
            tile = (actor.dungeon_level.value.
                    get_tile(actor.position.value))
            for piece in tile.get_all_pieces():
                for share_effect in piece.get_children_with_tag("entity_share_tile_effect"):
                    share_effect.share_tile_effect_tick(actor, gametime.normal_energy_gain)

    def tick(self):
        self._actors_tick()