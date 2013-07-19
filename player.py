import counter
import equipment
import missileaction
import monsterspawner
import colors
import dungeonlevel
import entity
import entityeffect
import numpy
import inventory
import messenger
import inputhandler
import menufactory
import statestack
import positionexaminer
import gametime
import geometry as geo


class Player(entity.Entity):
    def __init__(self, game_state):
        super(Player, self).__init__()
        self.hp = counter.Counter(10, 10)
        self._memory_map = []
        self._faction = entity.Faction.PLAYER
        self.inventory = inventory.Inventory(self)
        self._name = "CO"
        self._description = "The Brave"
        self._strength = 3
        self.game_state = game_state

    def _state_stack(self):
        return self.game_state.current_stack

    @property
    def strength(self):
        return self._strength

    @property
    def color_fg(self):
        if(self.has_status(entity.StatusFlags.INVISIBILE)):
            return colors.DB_VIKING
        return colors.DB_WHITE

    @property
    def symbol(self):
        return ord('@')

    def _signal_new_dungeon_level(self):
        self.set_memory_map_if_not_set(self.dungeon_level)

    def act(self):
        energy_spent = 0
        key = None
        while key is None:
            key = inputhandler.handler.get_keypress()
        if key in inputhandler.move_controls:
            dx, dy = inputhandler.move_controls[key]
            new_position = geo.add_2d(self.position, (dx, dy))
            move_succeded = self.try_step_to(new_position)
            if(move_succeded):
                energy_spent += self.movement_speed

        elif key == inputhandler.ESCAPE:
            self.kill_and_remove()
            energy_spent += gametime.single_turn

        elif key == inputhandler.REST:  # Rest
            energy_spent += gametime.single_turn

        elif key == inputhandler.EXAMINE:  # Rest
            game_gamestate = self._state_stack().peek()
            choose_target_prompt = statestack.StateStack()
            init_target = self.get_closest_seen_entity()
            if init_target is None:
                init_target = self.position
            else:
                init_target = init_target.position
            destination_selector =\
                positionexaminer.\
                MissileDestinationSelector(choose_target_prompt,
                                           self.position,
                                           self,
                                           game_gamestate,
                                           self._sight_radius,
                                           init_target=init_target)
            choose_target_prompt.push(destination_selector)
            choose_target_prompt.main_loop()

        elif key == inputhandler.PICKUP:  # Pick up
            item =\
                self.dungeon_level.get_tile(self.position).get_first_item()
            if(not item is None):
                pickup_succeded = self.inventory.try_add(item)
                if(pickup_succeded):
                    message = "Picked up: " + item.name
                    messenger.messenger.message(message)
                    energy_spent += gametime.single_turn
                else:
                    message = "Could not pick up: " + item.name +\
                        ", the inventory is full."
                    messenger.messenger.message(message)

        elif key == inputhandler.ONE:
            self.hurt(1)

        elif key == inputhandler.TWO:
            self.heal(1)

        elif key == inputhandler.THREE:
            effect = entityeffect.\
                Teleport(self, self,
                         time_to_live=1)
            self.add_entity_effect(effect)
            energy_spent += gametime.single_turn

        elif key == inputhandler.FOUR:
            invisibile_flag = entity.StatusFlags.INVISIBILE
            if(not self.has_status(invisibile_flag)):
                effect = entityeffect.\
                    StatusAdder(self, self,
                                invisibile_flag,
                                time_to_live=numpy.inf)
                self.add_entity_effect(effect)
            else:
                invisible_status = entity.StatusFlags.INVISIBILE
                effect = entityeffect.StatusRemover(self, self,
                                                    invisible_status,
                                                    time_to_live=1)
                self.add_entity_effect(effect)
            energy_spent += gametime.single_turn

        elif key == inputhandler.FIVE:
            monsterspawner.spawn_rat_man(self.dungeon_level)
            energy_spent += gametime.single_turn

        elif key == inputhandler.INVENTORY:
            if(not self.inventory.is_empty()):
                inventory_menu =\
                    menufactory.inventory_menu(self, self._state_stack())
                self._state_stack().push(inventory_menu)

        elif key == inputhandler.DESCEND:
            dungeon_feature = self.dungeon_level.get_tile(self.position)\
                .get_dungeon_feature()
            if(not dungeon_feature is None and
               len(dungeon_feature.player_actions) > 0):
                dungeon_feature.player_actions[0].act(source_entity=self,
                                                      target_entity=self)

        elif key == inputhandler.ENTER:
                context_menu = menufactory.context_menu(self,
                                                        self._state_stack())
                self._state_stack().push(context_menu)

        elif key == inputhandler.FIRE:

            game_state = self._state_stack().get_game_state()
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
                        energy_spent += gametime.single_turn
            else:
                rock_throwing = missileaction.PlayerThrowRockAction()
                if(rock_throwing.can_act(source_entity=self,
                                         game_state=game_state)):
                    throw_succeded = rock_throwing.act(source_entity=self,
                                                       game_state=game_state)
                    if throw_succeded:
                        energy_spent += gametime.single_turn
        self._state_stack().get_game_state().signal_should_redraw_screen()
        return energy_spent

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
