from actor import Actor
from entityeffect import Teleport, StatusAdder, StatusRemover
from equipment import EquipmentSlots
from missileaction import PlayerShootWeaponAction, PlayerThrowRockAction
from statusflags import StatusFlags
import console
import gametime
import geometry as geo
import inputhandler
import menufactory
import positionexaminer
import spawner


class InputActor(Actor):
    def __init__(self):
        super(InputActor, self).__init__()

    def act(self):
        self.parent.game_state.value.force_draw()

        self.newly_spent_energy = 0
        key = inputhandler.handler.get_keypress()
        if key is None:
            return 0
        if key in inputhandler.move_controls:
            dx, dy = inputhandler.move_controls[key]
            new_position = geo.add_2d(self.parent.position.value, (dx, dy))
            move_succeded = self.parent.mover.try_move_or_bump(new_position)
            if move_succeded:
                self.newly_spent_energy += self.parent.movement_speed.value
        elif key == inputhandler.ENTER:
            context_menu =\
                menufactory.context_menu(self.parent,
                                         self.parent.
                                         game_state.value.menu_prompt_stack)
            self.parent.game_state.value.start_prompt(context_menu)

        elif key == inputhandler.PRINTSCREEN:
            console.console.print_screen()
        elif key == inputhandler.TAB:
            command_list_state = self.parent.game_state.value.command_list_bar.active
            self.parent.game_state.value.command_list_bar.active = not command_list_state

        elif key == inputhandler.PICKUP:  # Pick up
            if self.parent.pick_up_item_action.can_act():
                self.parent.pick_up_item_action.act()
            else:
                self.parent.pick_up_item_action.print_player_error()
        elif key == inputhandler.FIRE:
            equipment = self.parent.equipment
            if equipment.slot_is_equiped(EquipmentSlots.RANGED_WEAPON):
                self.shoot_weapon()
        elif key == inputhandler.STONE:
            self.throw_rock()
        elif key == inputhandler.ESCAPE:
            self.parent.health.hp.set_min()
            self.newly_spent_energy += gametime.single_turn

        elif key == inputhandler.REST:  # Rest
            self.newly_spent_energy += gametime.single_turn

        elif key == inputhandler.EXAMINE:  # Rest
            init_target = self.parent.vision.get_closest_seen_entity()
            if init_target is None:
                init_target = self.parent.position.value
            else:
                init_target = init_target.position.value
            destination_selector =\
                positionexaminer.\
                MissileDestinationSelector(self.parent.game_state.
                                           value.menu_prompt_stack,
                                           self.parent.position.value,
                                           self.parent,
                                           self.parent.game_state.value,
                                           self.parent.sight_radius.value,
                                           init_target=init_target)
            self.parent.game_state.value.start_prompt(destination_selector)

        elif key == inputhandler.INVENTORY:
            if not self.parent.inventory.is_empty():
                menu = menufactory.inventory_menu(self.parent,
                                                  self.parent.game_state.
                                                  value.menu_prompt_stack)
                self.parent.game_state.value.start_prompt(menu)

        elif key == inputhandler.TWO:
            self.parent.health_modifier.heal(1)

        elif key == inputhandler.THREE:
            effect = Teleport(self.parent, time_to_live=1)
            self.parent.effect_queue.add(effect)
            self.newly_spent_energy += gametime.single_turn

        elif key == inputhandler.FOUR:
            invisibile_flag = StatusFlags.INVISIBILE
            if(not self.parent.status_flags.has_status(invisibile_flag)):
                effect = StatusAdder(self.parent,
                                     invisibile_flag,
                                     time_to_live=float("inf"))
                self.parent.effect_queue.add(effect)
            else:
                invisible_status = StatusFlags.INVISIBILE
                effect = StatusRemover(self.parent, invisible_status,
                                       time_to_live=1)
                self.parent.effect_queue.add(effect)
                self.newly_spent_energy += gametime.single_turn

        elif key == inputhandler.FIVE:
            spawner.spawn_rat_man(self.parent.dungeon_level.value,
                                  self.parent.game_state.value)
            self.newly_spent_energy += gametime.single_turn

        elif key == inputhandler.ZERO:
            self.parent.game_state.value.has_won = True
            self.newly_spent_energy += gametime.single_turn

        elif key == inputhandler.PRINTSCREEN:
            console.console.print_screen()

        if(self.has_sibling("dungeon_mask")):
            self.parent.dungeon_mask.update_fov()
        return self.newly_spent_energy

    def shoot_weapon(self):
        weapon = self.parent.equipment.get(EquipmentSlots.RANGED_WEAPON)
        shooting = PlayerShootWeaponAction(weapon)
        game_state = self.parent.game_state.value
        if shooting.can_act(source_entity=self.parent, game_state=game_state):
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
