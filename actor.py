from compositecore import Leaf
import turn
import gametime


class Actor(Leaf):
    def __init__(self, energy_recovery=gametime.normal_energy_gain):
        super(Actor, self).__init__()
        self.newly_spent_energy = 0
        self.energy = 0
        self.energy_recovery = gametime.normal_energy_gain
        self.component_type = "actor"

    def tick(self):
        self.energy += self.energy_recovery
        self._update_once_a_tick(self.energy_recovery)
        while self.energy > 0:
            self.energy -= self.act()
        turn.current_turn += 1

    def act(self):
        return 0

    def _update_once_a_tick(self, time_spent):
        pass
