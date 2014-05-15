from actor import Actor
from entityeffect import Teleport, StatusAdder, StatusRemover
from equipment import EquipmentSlots
from item import RangeWeaponType
import monster
import settings
import spawner
import menu
from missileaction import PlayerShootWeaponAction, PlayerSlingStoneAction
from statusflags import StatusFlags
import console
import gametime
import inputhandler
import menufactory
import positionexaminer
import util


class InputActor(Actor):
    def __init__(self):
        super(InputActor, self).__init__()

    def act(self):
        self.newly_spent_energy = 0

        self.handle_mouse_input()
        self.step_path()

        if len(self.parent.vision.get_seen_entities()) > 0:
            self.parent.path.clear()
        else:
            self.handle_auto_pick_up()

        if self.newly_spent_energy < 1:
            self.handle_keyboard_input()

        if self.has_sibling("dungeon_mask"):
            self.parent.dungeon_mask.update_fov()
        return self.newly_spent_energy

    def handle_mouse_input(self):
        inputhandler.handler.update_keys()
        mouse_position = inputhandler.handler.get_mouse_position()
        if not mouse_position is None:
            if inputhandler.handler.get_left_mouse_press():
                self.set_path_destination(self.parent.game_state.value.camera.
                                          screen_to_dungeon_position(mouse_position))

    def handle_context_action(self):
        context_menu_options = []
        player = self.parent
        state_stack = player.game_state.value.menu_prompt_stack
        stack_pop_function = menu.BackToGameFunction(state_stack)
        if player.pick_up_item_action.can_act(source_entity=self.parent,
                                              target_entity=self.parent,
                                              game_state=self.parent.game_state.value):
            pickup_option = player.pick_up_item_action.delayed_call(source_entity=player,
                                                                    target_entity=player,
                                                                    game_state=player.game_state.value)
            functions = [pickup_option, stack_pop_function]
            context_menu_options.append(menu.MenuOption(player.pick_up_item_action.name, functions))
        context_menu_options.extend(menufactory.get_dungeon_feature_menu_options(player, stack_pop_function))
        if len(context_menu_options) == 1 and context_menu_options[0].can_activate:
            context_menu_options[0].activate()
        elif len(context_menu_options) > 1:
            tile_menu = menufactory.get_menu_with_options(context_menu_options, state_stack)
            self.parent.game_state.value.start_prompt(tile_menu)

    def handle_auto_pick_up(self):
        dungeon_level = self.parent.dungeon_level.value
        position = self.parent.position.value
        item = dungeon_level.get_tile(position).get_first_item()
        if item and item.has("player_auto_pick_up"):
            self.handle_pick_up()

    def handle_dev_mode_commands(self, key):
        if key == inputhandler.TWO:
            self.parent.health_modifier.heal(300)

        elif key == inputhandler.THREE:
            effect = Teleport(self.parent, time_to_live=1)
            self.parent.effect_queue.add(effect)
            self.newly_spent_energy += gametime.single_turn

        elif key == inputhandler.FOUR:
            self.toggle_invisibility()

        elif key == inputhandler.FIVE:
            spawner.place_piece_on_random_walkable_tile(monster.new_ratman(self.parent.game_state.value),
                                                        self.parent.dungeon_level.value)
            self.newly_spent_energy += gametime.single_turn

        elif key == inputhandler.SIX:
            spawner.place_piece_on_random_walkable_tile(monster.new_ghost(self.parent.game_state.value),
                                                        self.parent.dungeon_level.value)
            self.newly_spent_energy += gametime.single_turn

        elif key == inputhandler.NINE:
            for entity in self.parent.dungeon_level.value.entities:
                if not entity is self.parent:
                    entity.health_modifier.kill()
            self.newly_spent_energy += gametime.single_turn
        elif key == inputhandler.ZERO:
            self.parent.game_state.value.has_won = True
            self.newly_spent_energy += gametime.single_turn
        elif key == inputhandler.END:
            self.newly_spent_energy += gametime.single_turn
            current_depth = self.parent.dungeon_level.value.depth
            next_dungeon_level = self.parent.dungeon_level.value.dungeon.get_dungeon_level(current_depth + 1)
            self.newly_spent_energy += gametime.single_turn
            if next_dungeon_level is None:
                return
            destination_position = next_dungeon_level.up_stairs[0].position.value
            self.parent.mover.move_push_over(destination_position, next_dungeon_level)

    def handle_pick_up(self):
        if self.parent.pick_up_item_action.can_act(source_entity=self.parent, target_entity=self.parent,
                                                   game_state=self.parent.game_state.value):
            self.parent.pick_up_item_action.act(source_entity=self.parent, target_entity=self.parent,
                                                game_state=self.parent.game_state.value)
        else:
            self.parent.pick_up_item_action.print_player_error(source_entity=self.parent, target_entity=self.parent,
                                                               game_state=self.parent.game_state.value)

    def handle_keyboard_input(self):
        key = inputhandler.handler.get_keypress()
        if key in inputhandler.move_controls or key in inputhandler.vi_move_controls:
            self.handle_move_input(key)
        elif key == inputhandler.ENTER:
            self.spawn_context_menu()
        elif key == inputhandler.PRINTSCREEN:
            console.console.print_screen()
        elif key == inputhandler.TAB:
            self.toggle_command_list()
        elif key == inputhandler.USE_PICK_UP:
            self.handle_context_action()
        elif key == inputhandler.PICKUP:  # Pick up
            self.handle_pick_up()
        elif key == inputhandler.FIRE:
            self.throw_or_shoot()
        elif key == inputhandler.ESCAPE:
            self.save_and_quit()
        elif key == inputhandler.REST:  # Rest
            self.newly_spent_energy += gametime.single_turn
        elif key == inputhandler.EXAMINE:
            self.start_examine()
        elif key == inputhandler.AUTO_EXPLORE:
            self.auto_explore()
        elif key == inputhandler.INVENTORY:
            self.try_open_inventory()
        elif key == inputhandler.EQUIPMENT:
            self.open_equipment()
        elif key == inputhandler.WEAR_WIELD:
            self.open_wear_wield_item_action_menu()
        elif key == inputhandler.DRINK:
            self.open_drink_item_action_menu()
        elif key == inputhandler.PRINTSCREEN:
            console.console.print_screen()
        if settings.DEV_MODE_FLAG:
            self.handle_dev_mode_commands(key)

    def step_path(self):
        if self.parent.path.has_path():
            self.newly_spent_energy = self.parent.path.try_step_path()

    def set_path_destination(self, destination):
        if not destination is None:
            if self.parent.memory_map.has_seen_position(destination):
                self.parent.path.compute_path(destination)
            else:
                self.parent.path.set_line_path(destination)

    def handle_move_input(self, key):
        if key in inputhandler.move_controls:
            direction = inputhandler.move_controls[key]
        else:
            direction = inputhandler.vi_move_controls[key]
        self.newly_spent_energy += self.parent.stepper.try_step_in_direction(direction)

    def spawn_context_menu(self):
        context_menu = menufactory.context_menu(self.parent, self.parent.game_state.value.menu_prompt_stack)
        self.parent.game_state.value.start_prompt(context_menu)

    def start_examine(self):
        destination_selector = positionexaminer.PositionSelector(self.parent.game_state.value.menu_prompt_stack,
                                                                 self.parent.position.value,
                                                                 self.parent.game_state.value)
        self.parent.game_state.value.start_prompt(destination_selector)
        destination = destination_selector.selected_position
        self.set_path_destination(destination)

    def try_open_inventory(self):
        if not self.parent.inventory.is_empty():
            inventory_menu = menufactory.inventory_menu(self.parent, self.parent.game_state.value.menu_prompt_stack)
            self.parent.game_state.value.start_prompt(inventory_menu)

    def open_equipment(self):
        equipment_menu = menufactory.equipment_menu(self.parent, self.parent.game_state.value.menu_prompt_stack)
        self.parent.game_state.value.start_prompt(equipment_menu)

    def auto_explore(self):
        closest_enemy = next((entity for entity in self.parent.vision.get_seen_entities_closest_first()
                             if not entity.position.value == self.parent.position.value), None)
        if closest_enemy and not closest_enemy.position.value == self.parent.position.value:
            self.parent.path.compute_path(closest_enemy.position.value)
        else:
            destination = util.get_closest_unseen_walkable_position(self.parent, self.parent.position.value,
                                                                    self.parent.dungeon_level.value)
            if destination:
                self.parent.path.compute_path(destination)

    def toggle_command_list(self):
        self.parent.game_state.value.command_list_bar.turn_page()

    def toggle_invisibility(self):
        invisible_flag = StatusFlags.INVISIBILE
        if not self.parent.status_flags.has_status(invisible_flag):
            effect = StatusAdder(self.parent, invisible_flag, time_to_live=float("inf"))
            self.parent.effect_queue.add(effect)
        else:
            invisible_status = StatusFlags.INVISIBILE
            effect = StatusRemover(self.parent, invisible_status, time_to_live=1)
            self.parent.effect_queue.add(effect)
            self.newly_spent_energy += gametime.single_turn

    def shoot_gun(self, weapon):
        shooting = PlayerShootWeaponAction(weapon)
        game_state = self.parent.game_state.value
        if shooting.can_act(source_entity=self.parent, game_state=game_state):
            shooting_succeded = shooting.act(source_entity=self.parent,
                                             game_state=game_state)
            if shooting_succeded:
                self.newly_spent_energy += gametime.single_turn

    def shoot_sling(self, weapon):
        shooting = PlayerSlingStoneAction(weapon)
        game_state = self.parent.game_state.value
        if shooting.can_act(source_entity=self.parent, game_state=game_state):
            shooting_succeded = shooting.act(source_entity=self.parent,
                                             game_state=game_state)
            if shooting_succeded:
                self.newly_spent_energy += gametime.single_turn

    def throw_or_shoot(self):
        if not self.parent.equipment.slot_is_equiped(EquipmentSlots.RANGED_WEAPON):
            self.throw_rock()
            return
        weapon = self.parent.equipment.get(EquipmentSlots.RANGED_WEAPON)
        if weapon.range_weapon_type.value == RangeWeaponType.GUN:
            self.shoot_gun(weapon)
        elif weapon.range_weapon_type.value == RangeWeaponType.SLING:
            self.shoot_sling(weapon)
        else:
            raise Exception("Tried to shoot weapon without range_weapon_type")

    def throw_rock(self):
        rock_throwing = self.parent.throw_stone_action
        game_state = self.parent.game_state.value
        if (rock_throwing.can_act(source_entity=self.parent,
                                  game_state=game_state)):
            rock_throwing.act(source_entity=self.parent,
                              game_state=game_state)

    def save_and_quit(self):
        save_quit_menu = menufactory.get_save_quit_menu(self.parent, self.parent.game_state.value.menu_prompt_stack)
        self.parent.game_state.value.start_prompt(save_quit_menu)

    def open_wear_wield_item_action_menu(self):
        reequip_tag = "reequip_action"
        if menufactory.has_item_with_action_tag(self.parent, reequip_tag):
            equip_menu = menufactory.filtered_by_action_item_menu(self.parent,
                                                                  self.parent.game_state.value.menu_prompt_stack,
                                                                  reequip_tag, "Wear / Wield")
            self.parent.game_state.value.start_prompt(equip_menu)

    def open_drink_item_action_menu(self):
        drink_tag = "drink_action"
        if menufactory.has_item_with_action_tag(self.parent, drink_tag):
            equip_menu = menufactory.filtered_by_action_item_menu(self.parent,
                                                                  self.parent.game_state.value.menu_prompt_stack,
                                                                  drink_tag, "Drink")
            self.parent.game_state.value.start_prompt(equip_menu)
