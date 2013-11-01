from compositecore import Leaf
import turn
import gametime


class Actor(Leaf):
    def __init__(self):
        super(Actor, self).__init__()
        self.component_type = "actor"
        self.newly_spent_energy = 0
        self.energy = 0
        self.energy_recovery = gametime.normal_energy_gain

    def tick(self):
        """
        Gives the actor an opportunity to act.

        The actor will act if it isn't in an energy debt.
        It also receives some energy.
        """
        self.energy += self.energy_recovery
        while self.energy > 0:
            self.energy -= self.act()
        turn.current_turn += 1

    def act(self):
        raise NotImplementedError("act method not implemented for parent:" +
                                  str(self.parent))


class DoNothingActor(Actor):
    """
    Entities with this actor will do nothing.
    """
    def __init__(self):
        super(DoNothingActor, self).__init__()

    def act(self):
        """
        Just returns energy spent, nothing is done.
        """
        return self.parent.movement_speed.value
