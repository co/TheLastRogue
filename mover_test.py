import unittest
import terrain
import dungeonlevel
from composite import Position, GamePieceType, Composite
from composite import DungeonLevel, StatusFlags
from mover import Mover


class TestComposition(unittest.TestCase):

    def setUp(self):
        dungeon1 = ["#####",
                    "#...#",
                    "#.#.#",
                    "#...#",
                    "#####"]
        self.dungeon_level = dungeonlevel.dungeon_level_from_lines(dungeon1)

        dungeon2 = ["#...#",
                    "..#..",
                    ".###.",
                    "..#..",
                    "#...#"]
        self.dungeon_level2 = dungeonlevel.dungeon_level_from_lines(dungeon2)
        self.wall_position = (2, 2)
        self.open_position = (1, 1)
        self.open_position2 = (3, 3)

    def set_up_new_entity_with_dungeon(self, dungeon_level):
        entity = Composite()
        entity.add_child(Mover())

        entity.add_child(Position())
        entity.add_child(GamePieceType
                         (GamePieceType.ENTITY))
        dungeon_level_component = DungeonLevel()
        dungeon_level_component.dungeon_level = dungeon_level
        entity.add_child(dungeon_level_component)

        return entity

    def test_can_fit_on_tile_should_retun_true_if_there_is_room(self):
        mover = self.set_up_new_entity_with_dungeon(self.dungeon_level)\
            .get_child_of_type(Mover)
        empty_tile = self.dungeon_level.get_tile(self.wall_position)
        self.assertTrue(mover._can_fit_on_tile(empty_tile))

    def test_can_pass_terrain_returns_false_if_terrain_is_none(self):
        mover = self.set_up_new_entity_with_dungeon(self.dungeon_level)\
            .get_child_of_type(Mover)
        self.assertFalse(mover._can_pass_terrain(None))

    def test_can_pass_terrain_returns_true_if_terrain_floor(self):
        mover = self.set_up_new_entity_with_dungeon(self.dungeon_level)\
            .get_child_of_type(Mover)
        floor = terrain.Floor()
        self.assertTrue(mover._can_pass_terrain(floor))

    def test_can_pass_door_if_entity_can_open_door(self):
        entity = self.set_up_new_entity_with_dungeon(self.dungeon_level)
        status_flags = StatusFlags()
        status_flags.add_status(StatusFlags.CAN_OPEN_DOORS)
        entity.add_child(status_flags)
        mover = entity.get_child_of_type(Mover)
        door = terrain.Door()
        door.close()
        self.assertTrue(mover._can_pass_terrain(door))

    def test_cant_pass_door_if_entity_cant_open_door(self):
        entity = self.set_up_new_entity_with_dungeon(self.dungeon_level)
        mover = entity.get_child_of_type(Mover)
        door = terrain.Door()
        door.close()
        self.assertFalse(mover._can_pass_terrain(door))

    def test_can_fit_on_tile_should_retun_false_if_there_is_not_room(self):
        blocked_position = (1, 1)
        blocking_entity =\
            self.set_up_new_entity_with_dungeon(self.dungeon_level)
        blocking_entity.get_child_of_type(Mover).\
            replace_move(blocked_position)

        mover = self.set_up_new_entity_with_dungeon(self.dungeon_level)\
            .get_child_of_type(Mover)
        blocked_tile = self.dungeon_level.get_tile(blocked_position)
        self.assertFalse(mover._can_fit_on_tile(blocked_tile))

    def test_can_move_to_wall_should_return_false(self):
        entity = self.set_up_new_entity_with_dungeon(self.dungeon_level)
        mover = entity.get_child_of_type(Mover)
        self.assertFalse(mover.can_move(self.wall_position))

    def test_can_move_to_open_space_should_return_true(self):
        entity = self.set_up_new_entity_with_dungeon(self.dungeon_level)
        mover = entity.get_child_of_type(Mover)
        self.assertTrue(mover.can_move(self.open_position))

    def test_try_remove_should_remove_entity_from_dungeon(self):
        entity = self.set_up_new_entity_with_dungeon(self.dungeon_level)
        mover = entity.get_child_of_type(Mover)
        self.assertTrue(mover.try_move(self.open_position))
        self.assertTrue(mover.try_remove_from_dungeon())
        print entity.get_child_of_type(DungeonLevel).dungeon_level
        self.assertTrue(entity.get_child_of_type(DungeonLevel).dungeon_level
                        is None)

    def test_try_move_should_move_entity_to_new_position(self):
        entity = self.set_up_new_entity_with_dungeon(self.dungeon_level)
        mover = entity.get_child_of_type(Mover)

        self.assertTrue(mover.try_move(self.open_position))

        self.assertTrue(entity.get_child_of_type(Position).position ==
                        self.open_position)
        self.assertTrue(self.dungeon_level.get_tile(self.open_position)
                        .get_entities()[0] is entity)

        self.assertTrue(mover.try_move(self.open_position2))
        self.assertTrue(entity.get_child_of_type(Position).position ==
                        self.open_position2)
        self.assertTrue(self.dungeon_level.get_tile(self.open_position2)
                        .get_entities()[0] is entity)

        self.assertFalse(entity.get_child_of_type(Position).position ==
                         self.open_position)
        self.assertFalse(self.dungeon_level.get_tile(self.open_position)
                         .has_entity())

    def test_try_move_to_new_dungeon_level_should_update_dungeon_level(self):
        entity = self.set_up_new_entity_with_dungeon(self.dungeon_level)
        mover = entity.get_child_of_type(Mover)

        self.assertTrue(mover.try_move(self.open_position, self.dungeon_level))
        self.assertTrue(entity.get_child_of_type(DungeonLevel).dungeon_level
                        is self.dungeon_level)

        self.assertTrue(mover.try_move(self.open_position,
                                       self.dungeon_level2))
        self.assertTrue(entity.get_child_of_type(DungeonLevel).dungeon_level
                        is self.dungeon_level2)

    def test_replace_move_should_replace_a_blocking_entity_on_move(self):
        entity_first = self.set_up_new_entity_with_dungeon(self.dungeon_level)
        self.assertTrue(entity_first.get_child_of_type(Mover)
                        .try_move(self.open_position))
        entity_second = self.set_up_new_entity_with_dungeon(self.dungeon_level)
        entity_second.get_child_of_type(Mover)\
            .replace_move(self.open_position)
        enteties_on_tile =\
            self.dungeon_level.get_tile(self.open_position).get_entities()
        self.assertFalse(any(entity is entity_first
                             for entity in enteties_on_tile))
        self.assertTrue(any(entity is entity_second
                            for entity in enteties_on_tile))
