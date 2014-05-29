import Status
import colors
from compositecore import Leaf
import turn
import gametime


class Actor(Leaf):
    def __init__(self):
        super(Actor, self).__init__()
        self.component_type = "actor"
        self.newly_spent_energy = 0
        self.energy = -gametime.single_turn
        self.energy_recovery = gametime.normal_energy_gain

    def tick(self):
        """
        Gives the actor an opportunity to act.

        The actor will act if it isn't in an energy debt.
        It also receives some energy.
        """
        if self._should_skip_me():
            self.energy - gametime.single_turn
            return
        self.energy += self.energy_recovery
        if self.energy > 0:
            turn.current_turn += 1
        while self.energy > 0:
            if self.parent.has("is_player"):
                self._post_player_act()
            self.energy -= self.act()

    def act(self):
        raise NotImplementedError("act method not implemented for parent:" +
                                  str(self.parent))

    def _should_skip_me(self):
        return self.parent.has("health") and self.parent.health.is_dead()

    def add_energy_spent(self, energy):
        self.newly_spent_energy += energy

    def _post_player_act(self):
        self.parent.game_state.value.force_draw()


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
        return gametime.single_turn


class StunnedActor(Actor):
    """
    Entities with this actor will do nothing.
    """
    def __init__(self):
        super(StunnedActor, self).__init__()

    def first_tick(self, time):
        if self.target_entity.has("status_bar"):
            self.parent.status_bar.add(Status.STUNNED_STATUS_ICON)

    def act(self):
        """
        Just returns energy spent, shows it's stunned.
        """
        self.parent.char_printer.append_fg_color_blink_frames([colors.CHAMPAGNE])
        return gametime.single_turn
