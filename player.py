import counter
import turn
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
import gamestate


class Player(entity.Entity):
    def __init__(self):
        super(Player, self).__init__()
        self.hp = counter.Counter(10, 10)
        self._memory_map = []
        self._faction = entity.FACTION_PLAYER
        self.inventory = inventory.Inventory(self)
        self._name = "CO"

    @property
    def color_fg(self):
        if(self.has_status(entity.StatusFlags.INVISIBILE)):
            return colors.DB_VIKING
        return colors.DB_WHITE

    @property
    def symbol(self):
        return ord('@')

    def update(self):
        done = False
        while not done:
            key = inputhandler.get_keypress()
            position = self.position
            if key in inputhandler.move_controls:
                dx, dy = inputhandler.move_controls[key]
                new_position = position + (dx, dy)
                move_succeded = self.try_move(new_position)
                done = move_succeded
                if(not done):
                    done = self.try_hit(new_position)

            elif key == inputhandler.ESCAPE:
                self.kill()
                done = True

            elif key == inputhandler.REST:  # Rest
                done = True

            elif key == inputhandler.PICKUP:  # Pick up
                item =\
                    self.dungeon_level.get_tile(self.position).get_first_item()
                if(not item is None):
                    pickup_succeded = self.inventory.try_add(item)
                    if(pickup_succeded):
                        message = "Picked up: " + item.name
                        messenger.messenger.message(message)
                        done = True
                    else:
                        message = "Could not pick up: " + item.name +\
                            ", the inventory is full."
                        messenger.messenger.message(message)

            elif key == inputhandler.HURT:
                self.hurt(1)

            elif key == inputhandler.TELEPORT:
                effect = entityeffect.\
                    Teleport(self, self,
                             time_to_live=1)
                self.add_entity_effect(effect)
                done = True

            elif key == inputhandler.HEAL:
                self.heal(1)

            elif key == inputhandler.INVISIBILITY:
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
                done = True

            elif key == inputhandler.SPAWN:
                monsterspawner.spawn_rat_man(self.dungeon_level)
                done = True

            elif key == inputhandler.INVENTORY:
                if(not self.inventory.is_empty()):
                    inventory_position =\
                        vector2d.Vector2D(settings.WINDOW_WIDTH - 24, 0)
                    inventory_menu = menu.InventoryMenu(inventory_position,
                                                        settings.WINDOW_WIDTH,
                                                        settings.WINDOW_HEIGHT,
                                                        self.inventory)
                    gamestate.game_state_stack.push(inventory_menu)
            if(done):
                turn.current_turn += 1
            return done

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
        self._memory_map[depth].tile_matrix[position.y][position.x]\
            = tile.copy()
