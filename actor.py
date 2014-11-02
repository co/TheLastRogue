import Status
import colors
from compositecore import Leaf
import turn
import gametime


class Actor(Leaf):
    def __init__(self):
        super(Actor, self).__init__()
        self.component_type = "actor"

        # used by actor to keep track of how much energy was spent this tick.
        self.newly_spent_energy = 0
        self.energy_recovery = gametime.normal_energy_gain

    @property
    def ticks_per_turn(self):
        return gametime.single_turn / self.energy_recovery

    def tick(self):
        """
        Gives the actor an opportunity to act.

        The actor will act if it isn't in an energy debt.
        It also receives some energy.
        """
        if self._should_skip_me():
            self.parent.energy.value - gametime.single_turn
            return
        self.parent.energy.value += self.energy_recovery
        self.check_new_turn()
        need_draw = False
        while self.parent.energy.value > 0:
            if need_draw and self.parent.has("is_player"):  # need a draw in this loop to draw animations but,
                                                                # can skip first draw check_new_turn will draw.
                self.parent.game_state.value.force_draw()
            need_draw = True
            self.parent.energy.value -= self.act()

    def check_new_turn(self):
        if self.parent.has("is_player"):
            turn.ticks_this_turn += 1
            if turn.ticks_this_turn > self.ticks_per_turn:
                turn.current_turn += 1
                turn.ticks_this_turn = 0
                self.parent.game_state.value.force_draw()

    def act(self):
        raise NotImplementedError("act method not implemented for parent:" +
                                  str(self.parent))

    def _should_skip_me(self):
        return self.parent.has("health") and self.parent.health.is_dead()

    def add_energy_spent(self, energy):
        self.newly_spent_energy += energy


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

    def on_tick(self, time):
        if self.parent.has("status_bar"):
            self.parent.status_bar.add(Status.STUNNED_STATUS_DESCRIPTION)

    def act(self):
        """
        Just returns energy spent, shows it's stunned.
        """
        self.parent.char_printer.append_fg_color_blink_frames([colors.CHAMPAGNE])
        return gametime.single_turn


class ParalyzedActor(Actor):
    """
    Entities with this actor will do nothing.
    """
    def __init__(self):
        super(ParalyzedActor, self).__init__()

    def on_tick(self, time):
        if self.parent.has("status_bar"):
            self.parent.status_bar.add(Status.PARALYZED_STATUS_DESCRIPTION)

    def act(self):
        """
        Just returns energy spent, shows it's stunned.
        """
        self.parent.char_printer.append_fg_color_blink_frames([colors.YELLOW])
        return gametime.single_turn