import menufactory
import console
import geometry as geo
import inputhandler
import gametime
from actor import Actor
from equipment import EquipmentSlots
from missileaction import PlayerShootWeaponAction, PlayerThrowRockAction


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
            move_succeded = self.parent.mover.try_move_or_bump(new_position)
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
        elif key == inputhandler.FIRE:
            equipment = self.parent.equipment
            if(equipment.slot_is_equiped(EquipmentSlots.RANGED_WEAPON)):
                self.shoot_weapon()
            else:
                self.throw_rock()

        elif key == inputhandler.PRINTSCREEN:
            console.console.print_screen()
        return self.newly_spent_energy

    def shoot_weapon(self):
        weapon = self.parent.equipment.get(EquipmentSlots.RANGED_WEAPON)
        shooting = PlayerShootWeaponAction(weapon)
        game_state = self.parent.game_state.value
        if(shooting.can_act(source_entity=self.parent, game_state=game_state)):
            shooting_succeded = shooting.act(source_entity=self.parent,
                                             game_state=game_state)
            if shooting_succeded:
                self.newly_spent_energy += gametime.single_turn

    def throw_rock(self):
        rock_throwing = PlayerThrowRockAction()
        game_state = self.parent.game_state.value
        if(rock_throwing.can_act(source_entity=self.parent,
                                 game_state=game_state)):
            rock_throwing.act(source_entity=self.parent,
                              game_state=game_state)
