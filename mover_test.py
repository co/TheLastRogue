import unittest
from compositecore import Composite
from mover import Mover
from position import Position, DungeonLevel
from stats import GamePieceTypes, DataTypes, DataPoint
from statusflags import StatusFlags
import dungeonlevelfactory
import terrain
from text import Description


dummy_player = Composite()
dummy_player.set_child(StatusFlags([StatusFlags.CAN_OPEN_DOORS]))
dummy_player.set_child(Mover())
dummy_player.set_child(Description("player_dummy", "Just a dummy used for instead of player for calculations."))

dummy_flyer = Composite()
dummy_flyer.set_child(StatusFlags([StatusFlags.FLYING]))
dummy_flyer.set_child(Mover())
dummy_flyer.set_child(Description("flyer_dummy", "Just a dummy used for instead a flyer for calculations."))


class TestComposition(unittest.TestCase):

    def setUp(self):
        dungeon1 = ["#####",
                    "#...#",
                    "#.#.#",
                    "#...#",
                    "#####"]
        self.dungeon_level =\
            dungeonlevelfactory.dungeon_level_from_lines(dungeon1)

        dungeon2 = ["#...#",
                    "..#..",
                    ".###.",
                    "..#..",
                    "#...#"]
        self.dungeon_level2 =\
            dungeonlevelfactory.dungeon_level_from_lines(dungeon2)
        self.wall_position = (2, 2)
        self.open_position = (1, 1)
        self.open_position2 = (3, 3)

    def set_up_new_entity_with_dungeon(self, dungeon_level):
        entity = Composite()
        entity.set_child(Mover())

        entity.set_child(Position())
        entity.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.ENTITY))
        dungeon_level_component = DungeonLevel()
        dungeon_level_component.value = dungeon_level
        entity.set_child(dungeon_level_component)

        return entity

    def test_can_fit_on_tile_should_retun_true_if_there_is_room(self):
        entity = self.set_up_new_entity_with_dungeon(self.dungeon_level)
        empty_tile = self.dungeon_level.get_tile(self.wall_position)
        self.assertTrue(entity.mover._can_fit_on_tile(empty_tile))

    def test_can_pass_terrain_returns_true_if_terrain_is_none(self):
        entity = self.set_up_new_entity_with_dungeon(self.dungeon_level)
        self.assertTrue(entity.mover.can_pass_terrain(None))

    def test_can_pass_terrain_returns_true_if_terrain_floor(self):
        entity = self.set_up_new_entity_with_dungeon(self.dungeon_level)
        floor = terrain.Floor()
        self.assertTrue(entity.mover.can_pass_terrain(floor))

    def test_can_pass_door_if_entity_can_open_door(self):
        entity = self.set_up_new_entity_with_dungeon(self.dungeon_level)
        status_flags = StatusFlags([StatusFlags.CAN_OPEN_DOORS])
        entity.set_child(status_flags)
        door = terrain.Door()
        door_position = (2, 1)
        door.mover.replace_move(door_position, self.dungeon_level)
        self.assertTrue(door.bump_action.can_bump(entity))
        door.bump_action.bump(entity)
        self.assertTrue(entity.mover.can_pass_terrain(door))

    def test_cant_move_to_door_if_it_is_closed(self):
        entity = self.set_up_new_entity_with_dungeon(self.dungeon_level)
        entity.set_child(StatusFlags([StatusFlags.CAN_OPEN_DOORS]))
        door = terrain.Door()
        door_position = (2, 1)
        door.mover.replace_move(door_position, self.dungeon_level)
        self.assertFalse(entity.mover.try_move(door_position))

    def test_flying_entity_can_move_to_chasm(self):
        entity = self.set_up_new_entity_with_dungeon(self.dungeon_level)
        entity.set_child(StatusFlags([StatusFlags.FLYING]))
        chasm_position = (2, 1)
        chasm = terrain.Chasm()
        chasm.mover.replace_move(chasm_position, self.dungeon_level)
        self.assertTrue(entity.mover.try_move(chasm_position))

    def test_can_move_to_door_if_it_is_opened(self):
        entity = self.set_up_new_entity_with_dungeon(self.dungeon_level)
        door = terrain.Door()
        door.mover.replace_move((2, 1), self.dungeon_level)
        door.open_door_action.open_door()
        self.assertTrue(entity.mover.try_move((2, 1)))

    def test_can_fit_on_tile_should_return_false_if_there_is_not_room(self):
        blocked_position = (1, 1)
        blocking_entity =\
            self.set_up_new_entity_with_dungeon(self.dungeon_level)
        blocking_entity.mover.replace_move(blocked_position)

        entity = self.set_up_new_entity_with_dungeon(self.dungeon_level)
        blocked_tile = self.dungeon_level.get_tile(blocked_position)
        self.assertFalse(entity.mover._can_fit_on_tile(blocked_tile))

    def test_can_move_to_wall_should_return_false(self):
        entity = self.set_up_new_entity_with_dungeon(self.dungeon_level)
        self.assertFalse(entity.mover.can_move(self.wall_position))

    def test_can_move_to_open_space_should_return_true(self):
        entity = self.set_up_new_entity_with_dungeon(self.dungeon_level)
        self.assertTrue(entity.mover.can_move(self.open_position))

    def test_try_remove_should_remove_entity_from_dungeon(self):
        entity = self.set_up_new_entity_with_dungeon(self.dungeon_level)
        self.assertTrue(entity.mover.try_move(self.open_position))
        self.assertTrue(entity.mover.try_remove_from_dungeon())
        self.assertTrue(entity.has("dungeon_level"))
        self.assertTrue(entity.dungeon_level.value is None)

    def test_try_move_should_move_entity_to_new_position(self):
        entity = self.set_up_new_entity_with_dungeon(self.dungeon_level)

        self.assertTrue(entity.mover.try_move(self.open_position))

        self.assertTrue(entity.position.value == self.open_position)
        self.assertTrue(self.dungeon_level.get_tile(self.open_position)
                        .get_entities()[0] is entity)

        self.assertTrue(entity.mover.try_move(self.open_position2))
        self.assertTrue(entity.position.value == self.open_position2)
        self.assertTrue(self.dungeon_level.get_tile(self.open_position2)
                        .get_entities()[0] is entity)

        self.assertFalse(entity.position.value == self.open_position)
        self.assertFalse(self.dungeon_level.get_tile(self.open_position)
                         .has_entity())

    def test_try_move_to_new_dungeon_level_should_update_dungeon_level(self):
        entity = self.set_up_new_entity_with_dungeon(self.dungeon_level)

        self.assertTrue(entity.mover.try_move(self.open_position,
                                              self.dungeon_level))
        self.assertTrue(entity.dungeon_level.value is self.dungeon_level)

        self.assertTrue(entity.mover.try_move(self.open_position,
                                              self.dungeon_level2))
        self.assertTrue(entity.dungeon_level.value is self.dungeon_level2)

    def test_try_move_to_dungeon_level_should_handle_no_previous_dungeon(self):
        entity = self.set_up_new_entity_with_dungeon(None)
        self.assertTrue(entity.mover.try_move(self.open_position,
                                              self.dungeon_level))
        self.assertTrue(entity.dungeon_level.value is self.dungeon_level)

    def test_replace_move_should_replace_a_blocking_entity_on_move(self):
        entity_first = self.set_up_new_entity_with_dungeon(self.dungeon_level)
        self.assertTrue(entity_first.mover
                        .try_move(self.open_position))
        entity_second = self.set_up_new_entity_with_dungeon(self.dungeon_level)
        entity_second.mover.replace_move(self.open_position)
        enteties_on_tile =\
            self.dungeon_level.get_tile(self.open_position).get_entities()
        self.assertFalse(any(entity is entity_first
                             for entity in enteties_on_tile))
        self.assertTrue(any(entity is entity_second
                            for entity in enteties_on_tile))

    # can pass terrain tests.
    def test_not_flying_cant_pass_chasm(self):
        self.assertFalse(dummy_player.mover.can_pass_terrain(terrain.Chasm()))

    def test_flying_can_pass_chasm(self):
        self.assertTrue(dummy_flyer.mover.can_pass_terrain(terrain.Chasm()))