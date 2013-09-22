import unittest
import terrain
import dungeonlevel
import composite


class TestComposition(unittest.TestCase):

    def setUp(self):
        dungeon = ["#####",
                   "#...#",
                   "#.#.#",
                   "#...#",
                   "#####"]
        self.dungeon_level = dungeonlevel.dungeon_level_from_lines(dungeon)
        self.wall_position = (2, 2)
        self.open_position = (3, 2)

    def set_up_new_entity(self, dungeon_level):
        entity = composite.Composite()
        entity.add_child(composite.Mover())

    def set_up_new_entity_with_dungeon(self, dungeon_level):
        entity = composite.Composite()
        entity.add_child(composite.Mover())

        entity.add_child(composite.Position())
        entity.add_child(composite.GamePieceType
                         (composite.GamePieceType.ENTITY))
        dungeon_level_component = composite.DungeonLevel()
        dungeon_level_component.dungeon_level = dungeon_level
        entity.add_child(dungeon_level_component)

        return entity

    def test_can_fit_on_tile_should_retun_true_if_there_is_room(self):
        mover = self.set_up_new_entity_with_dungeon(self.dungeon_level)\
            .get_child(composite.Mover)
        empty_tile = self.dungeon_level.get_tile(self.wall_position)
        self.assertTrue(mover._can_fit_on_tile(empty_tile))

    def test_can_pass_terrain_returns_false_if_terrain_is_none(self):
        mover = self.set_up_new_entity_with_dungeon(self.dungeon_level)\
            .get_child(composite.Mover)
        self.assertFalse(mover._can_pass_terrain(None))

    def test_can_pass_terrain_returns_true_if_terrain_floor(self):
        mover = self.set_up_new_entity_with_dungeon(self.dungeon_level)\
            .get_child(composite.Mover)
        floor = terrain.Floor()
        self.assertTrue(mover._can_pass_terrain(floor))

    def test_can_pass_door_if_entity_can_open_door(self):
        entity = self.set_up_new_entity_with_dungeon(self.dungeon_level)
        status_flags = composite.StatusFlags()
        status_flags.add_status(composite.StatusFlags.CAN_OPEN_DOORS)
        entity.add_child(status_flags)
        mover = entity.get_child(composite.Mover)
        door = terrain.Door()
        door.close()
        self.assertTrue(mover._can_pass_terrain(door))

    def test_cant_pass_door_if_entity_cant_open_door(self):
        entity = self.set_up_new_entity_with_dungeon(self.dungeon_level)
        mover = entity.get_child(composite.Mover)
        door = terrain.Door()
        door.close()
        self.assertFalse(mover._can_pass_terrain(door))

    def test_can_fit_on_tile_should_retun_false_if_there_is_not_room(self):
        blocked_position = (1, 1)
        blocking_entity =\
            self.set_up_new_entity_with_dungeon(self.dungeon_level)
        blocking_entity.get_child(composite.Mover).\
            replace_move(blocked_position)

        mover = self.set_up_new_entity_with_dungeon(self.dungeon_level)\
            .get_child(composite.Mover)
        blocked_tile = self.dungeon_level.get_tile(blocked_position)
        self.assertFalse(mover._can_fit_on_tile(blocked_tile))

    def test_can_move_to_wall_should_return_false(self):
        entity = self.set_up_new_entity_with_dungeon(self.dungeon_level)
        mover = entity.get_child(composite.Mover)
        self.assertFalse(mover.can_move(self.wall_position))

    def test_can_move_to_open_space_should_return_true(self):
        entity = self.set_up_new_entity_with_dungeon(self.dungeon_level)
        mover = entity.get_child(composite.Mover)
        self.assertTrue(mover.can_move(self.open_position))

    def test_try_remove_should_remove_entity_from_dungeon(self):
        mover = self.set_up_new_entity_with_dungeon(self.dungeon_level)\
            .get_child(composite.Mover)
        self.assertTrue(mover.try_move(self.open_position))
        self.assertTrue(mover.try_remove_from_dungeon())
