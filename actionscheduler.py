from collections import deque


class ActionScheduler(object):
    def __init__(self):
        self._actors = deque()

    @property
    def entities(self):
        return [actor for actor in self._actors]

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
            actor.before_tick(self.energy_recovery)
            actor.on_tick(self.energy_recovery)
            actor.tick()
            self._actors.rotate()

    def tick(self):
        self._actors_tick()
