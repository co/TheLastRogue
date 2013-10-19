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
#
#    def try_move(self, new_position, new_dungeon_level=None):
#        """
#        Will attempt to move the actor to a new dungeon_level/position.
#        If the move is successful return true otherwise false.
#        """
#        if(new_dungeon_level is None):
#            new_dungeon_level = self.dungeon_level
#        old_dungeon_level = self.dungeon_level
#        move_succeded = super(Actor, self).\
#            try_move(new_position, new_dungeon_level)
#        if(move_succeded):
#            if(not old_dungeon_level is None and
#               (not old_dungeon_level is new_dungeon_level)):
#                old_dungeon_level.remove_actor_if_present(self)
#            new_dungeon_level.add_actor_if_not_present(self)
#            self.update_fov()
#        return move_succeded
#
#    def try_remove_from_dungeon(self):
#        """
#        Will attempt to remove the actor from the dungeon_level/position.
#        If the remove is successful return true otherwise false.
#        """
#        old_dungeon_level = self.dungeon_level
#        remove_succeded = super(Actor, self).\
#            try_remove_from_dungeon()
#        if(remove_succeded and (not old_dungeon_level is None)):
#            old_dungeon_level.remove_actor_if_present(self)
#        return remove_succeded

    def tick(self):
        self.energy += self.energy_recovery
        self.parent.on_tick(self.energy_recovery)
        while self.energy > 0:
            self.energy -= self.act()
        turn.current_turn += 1

    def act(self):
        raise NotImplementedError("act method not implemented for parent:" +
                                  str(self.parent))
