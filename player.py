import counter
import cloud
import console
import symbol
import action
import equipment
import missileaction
import spawner
import colors
import dungeonlevel
import entity
import entityeffect
import inventory
import inputhandler
import menufactory
import positionexaminer
import gametime
import geometry as geo


# got data for all fields
class Player(entity.Entity):
    def __init__(self, game_state):
        super(Player, self).__init__(game_state)
        self.hp = counter.Counter(10, 10)
        self._memory_map = []
        self._faction = entity.Faction.PLAYER
        self.inventory = inventory.Inventory(self)
        self._name = "CO"
        self._description = "The Brave"
        self.strength = 3
        self.gfx_char.color_fg = colors.WHITE
        self.gfx_char.symbol = symbol.GUNSLINGER_THIN

    def _signal_new_dungeon_level(self):
        self.set_memory_map_if_not_set(self.dungeon_level)

    def act(self):
        #If the player is about to act, the latest state should be shown.
        self.game_state.force_draw()

        self.newly_spent_energy = 0
        key = inputhandler.handler.get_keypress()
        if(key is None):
            return 0
        if key in inputhandler.move_controls:
            dx, dy = inputhandler.move_controls[key]
            new_position = geo.add_2d(self.position, (dx, dy))
            move_succeded = self.try_move_to(new_position)
            if(move_succeded):
                self.newly_spent_energy += self.movement_speed

        elif key == inputhandler.ESCAPE:
            self.kill_and_remove()
            self.newly_spent_energy += gametime.single_turn

        elif key == inputhandler.REST:  # Rest
            self.newly_spent_energy += gametime.single_turn

        elif key == inputhandler.EXAMINE:  # Rest
            init_target = self.get_closest_seen_entity()
            if init_target is None:
                init_target = self.position
            else:
                init_target = init_target.position
            destination_selector =\
                positionexaminer.\
                MissileDestinationSelector(self.game_state.menu_prompt_stack,
                                           self.position,
                                           self,
                                           self.game_state,
                                           self._sight_radius,
                                           init_target=init_target)
            self.game_state.start_prompt(destination_selector)

        elif key == inputhandler.PICKUP:  # Pick up
            pick_up_action = action.PickUpItemAction()
            if(pick_up_action.can_act(source_entity=self, target_entity=self)):
                pick_up_action.act(source_entity=self, target_entity=self)
            else:
                pick_up_action.print_player_error(source_entity=self,
                                                  target_entity=self)

        elif key == inputhandler.ONE:
            steam_cloud = cloud.Steam(50)
            steam_cloud.try_move(self.position, self.dungeon_level)

        elif key == inputhandler.TWO:
            self.heal(1)

        elif key == inputhandler.THREE:
            effect = entityeffect.\
                Teleport(self, self,
                         time_to_live=1)
            self.add_entity_effect(effect)
            self.newly_spent_energy += gametime.single_turn

        elif key == inputhandler.FOUR:
            invisibile_flag = entity.StatusFlags.INVISIBILE
            if(not self.has_status(invisibile_flag)):
                effect = entityeffect.\
                    StatusAdder(self, self,
                                invisibile_flag,
                                time_to_live=float("inf"))
                self.add_entity_effect(effect)
            else:
                invisible_status = entity.StatusFlags.INVISIBILE
                effect = entityeffect.StatusRemover(self, self,
                                                    invisible_status,
                                                    time_to_live=1)
                self.add_entity_effect(effect)
            self.newly_spent_energy += gametime.single_turn

        elif key == inputhandler.FIVE:
            spawner.spawn_rat_man(self.dungeon_level, self.game_state)
            self.newly_spent_energy += gametime.single_turn

        elif key == inputhandler.INVENTORY:
            if(not self.inventory.is_empty()):
                menu = menufactory.inventory_menu(self,
                                                  self.game_state.
                                                  menu_prompt_stack)
                self.game_state.start_prompt(menu)

        elif key == inputhandler.DESCEND:
            dungeon_feature = self.dungeon_level.get_tile(self.position)\
                .get_dungeon_feature()
            if(not dungeon_feature is None and
               len(dungeon_feature.player_actions) > 0):
                dungeon_feature.player_actions[0].act(source_entity=self,
                                                      target_entity=self)

        elif key == inputhandler.ENTER:
            context_menu =\
                menufactory.context_menu(self,
                                         self.game_state.menu_prompt_stack)
            self.game_state.start_prompt(context_menu)

        elif key == inputhandler.FIRE:

            game_state = self.state_stack.get_game_state()
            if(self.equipment.slot_is_equiped
               (equipment.EquipmentSlots.RANGED_WEAPON)):
                weapon =\
                    self.equipment.get(equipment.EquipmentSlots.RANGED_WEAPON)
                shooting = missileaction.PlayerShootWeaponAction(weapon)
                if(shooting.can_act(source_entity=self,
                                    game_state=game_state)):
                    shooting_succeded = shooting.act(source_entity=self,
                                                     game_state=game_state)
                    if shooting_succeded:
                        self.newly_spent_energy += gametime.single_turn
            else:
                rock_throwing = missileaction.PlayerThrowRockAction()
                if(rock_throwing.can_act(source_entity=self,
                                         game_state=game_state)):
                    rock_throwing.act(source_entity=self,
                                      game_state=game_state)
        elif key == inputhandler.PRINTSCREEN:
            console.console.print_screen()
        return self.newly_spent_energy

    def kill_and_remove(self):
        self.hp.set_min()

    def get_memory_of_map(self, dungeon_level):
        self.set_memory_map_if_not_set(dungeon_level)
        return self._memory_map[dungeon_level.depth]

    def set_memory_map_if_not_set(self, dungeon_level):
        depth = dungeon_level.depth
        while(len(self._memory_map) <= depth):
            self._memory_map.append(None)
        if(self._memory_map[depth] is None):
            self._memory_map[depth] = dungeonlevel.unknown_level_map(
                dungeon_level.width, dungeon_level.height, dungeon_level.depth)

    def update_memory_of_tile(self, tile, position, depth):
        if (tile.get_first_entity() is self):
            return  # No need to remember where you was, you are not there.
        self.set_memory_map_if_not_set(self.dungeon_level)
        x, y = position
        self._memory_map[depth].tile_matrix[y][x] = tile.copy()
