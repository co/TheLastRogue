import counter
import monsterspawner
import colors
import dungeonlevel
import entity
import entityeffect
import numpy
import inventory
import messenger
import inputhandler
import menu
import vector2d
import settings
import statestack
import positionexaminer


class Player(entity.Entity):
    def __init__(self, game_state):
        super(Player, self).__init__()
        self.hp = counter.Counter(10, 10)
        self._memory_map = []
        self._faction = entity.Faction.PLAYER
        self.inventory = inventory.Inventory(self)
        self._name = "CO"
        self._description = "The Brave"
        self.turn_over = False
        self._strength = 3
        self.game_state = game_state

    def _current_state_stack(self):
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

    def update(self):
        self.turn_over = False
        key = inputhandler.get_keypress()
        position = self.position
        if key in inputhandler.move_controls:
            dx = inputhandler.move_controls[key].x
            dy = inputhandler.move_controls[key].y
            new_position = position + (dx, dy)
            move_succeded = self.try_step_to(new_position)
            self.turn_over = move_succeded

        elif key == inputhandler.ESCAPE:
            self.kill()
            self.turn_over = True

        elif key == inputhandler.REST:  # Rest
            self.turn_over = True

        elif key == inputhandler.EXAMINE:  # Rest
            game_gamestate = self._current_state_stack().peek()
            choose_target_prompt = statestack.StateStack()
            destination_selector =\
                positionexaminer.\
                MissileDestinationSelector(choose_target_prompt,
                                           self.position.copy(),
                                           self,
                                           game_gamestate,
                                           self._sight_radius)
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
                    self.turn_over = True
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
            self.turn_over = True

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
            self.turn_over = True

        elif key == inputhandler.FIVE:
            monsterspawner.spawn_rat_man(self.dungeon_level)
            self.turn_over = True

        elif key == inputhandler.INVENTORY:
            if(not self.inventory.is_empty()):
                inventory_position =\
                    vector2d.Vector2D(settings.WINDOW_WIDTH - 24, 0)
                inventory_menu = menu.InventoryMenu(inventory_position,
                                                    settings.WINDOW_WIDTH,
                                                    settings.WINDOW_HEIGHT,
                                                    self)
                self._current_state_stack().push(inventory_menu)

        elif key == inputhandler.DESCEND:
            dungeon_feature = self.dungeon_level.get_tile(self.position)\
                .get_dungeon_feature()
            if(not dungeon_feature is None and
               len(dungeon_feature.player_actions) > 0):
                dungeon_feature.player_actions[0].act(source_entity=self,
                                                      target_entity=self)

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
        self._memory_map[depth].tile_matrix[position.y][position.x]\
            = tile.copy()
