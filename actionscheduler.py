from collections import deque
import gametime


class ActionScheduler(object):
    def __init__(self):
        self._actors = deque()

    @property
    def entities(self): # All monsters have health
        return [actor for actor in self._actors if actor.has("health")]

    @property
    def actors(self):
        return list(self._actors)

    def register(self, actor):
        self._actors.append(actor)

    def release(self, actor):
        self._actors.remove(actor)

    def _actors_tick(self):
        if len(self._actors) > 0:
            actor = self._actors[0].actor
            actor.parent.before_tick(gametime.normal_energy_gain)
            self.on_tick(actor)
            actor.tick()
            actor.parent.on_tick(gametime.normal_energy_gain)
            actor.parent.after_tick(gametime.normal_energy_gain)
            self._actors.rotate()

    def on_tick(self, current_actor):
        self.sharing_tile_effects_tick(current_actor.parent)

    def sharing_tile_effects_tick(self, current_piece):
        if(current_piece.has("dungeon_level") and
           current_piece.has("position")):
            tile = (current_piece.dungeon_level.value.
                    get_tile(current_piece.position.value))
            for piece in tile.get_all_pieces():
                for share_effect in piece.get_children_with_tag("entity_share_tile_effect"):
                    share_effect.share_tile_effect_tick(current_piece, gametime.normal_energy_gain)

    def tick(self):
        self._actors_tick()
