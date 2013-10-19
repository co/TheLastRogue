import menufactory
from actor import Actor
import console
import geometry as geo
import inputhandler


class InputActor(Actor):
    def __init__(self):
        super(InputActor, self).__init__()

    def act(self):
        self.parent.game_state.value.force_draw()

        self.newly_spent_energy = 0
        key = inputhandler.handler.get_keypress()
        if(key is None):
            return 0
        if key in inputhandler.move_controls:
            dx, dy = inputhandler.move_controls[key]
            new_position = geo.add_2d(self.parent.position.value, (dx, dy))
            move_succeded = self.parent.mover.try_move(new_position)
            if(move_succeded):
                self.newly_spent_energy += self.parent.movement_speed.value
        elif key == inputhandler.ENTER:
            context_menu =\
                menufactory.context_menu(self.parent,
                                         self.parent.
                                         game_state.value.menu_prompt_stack)
            self.parent.game_state.value.start_prompt(context_menu)

        elif key == inputhandler.PRINTSCREEN:
            console.console.print_screen()
        elif key == inputhandler.PICKUP:  # Pick up
            if(self.parent.pick_up_item_action.can_act()):
                self.parent.pick_up_item_action.act()
            else:
                self.parent.pick_up_item_action.print_player_error()

        return self.newly_spent_energy
