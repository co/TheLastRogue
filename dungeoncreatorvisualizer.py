import dungeongenerator as dgen
import geometry as geo
import camera
from console import console
import direction
import inputhandler
import state
import terrain


class DungeonCreatorVisualizer(state.State):
    def __init__(self):
        super(DungeonCreatorVisualizer, self).__init__()
        self.dungeon_level = dgen.get_full_wall_dungeon(70, 55, 0)
        self.camera = camera.Camera(geo.zero2d(), geo.zero2d())

    def fill_dungeon(self):
        width = self.dungeon_level.width
        height = self.dungeon_level.height
        self.dungeon_level = dgen.get_full_wall_dungeon(width, height, 0)

    def draw(self):
        self.dungeon_level.draw_everything(self.camera)
        console.flush()

    def update(self):
        self.handle_input()

    def generate_dungeon_level(self):
        size = 1200
        depth = 1
        self.dungeon_level = dgen.generate_dungeon_exploded_rooms(size, depth)

    def random_exlosion(self):
        dungeon_level = self.dungeon_level
        center_position = (dungeon_level.width / 2, dungeon_level.height / 2)
        brush = dgen.SinglePointBrush(dgen.ReplaceTerrain(terrain.Floor))
        end_condition = dgen.CountDownCondition(dungeon_level.width *
                                                dungeon_level.height * 0.1)
        move_list = list(direction.AXIS_DIRECTIONS)
        dgen.random_explosion(dungeon_level, center_position, brush,
                             end_condition, move_list)

    def drunkard_walk(self):
        dungeon_level = self.dungeon_level
        center_position = (dungeon_level.width / 2, dungeon_level.height / 2)
        brush = dgen.SinglePointBrush(dgen.ReplaceTerrain(terrain.Floor))
        end_condition = dgen.CountDownCondition(dungeon_level.width *
                                                dungeon_level.height * 0.2)
        move_list = list(direction.DIRECTIONS)
        dgen.drunkard_walk(dungeon_level, center_position, brush,
                           end_condition, move_list)

    def drunkard_walk2(self):
        dungeon_level = self.dungeon_level
        center_position = (dungeon_level.width / 2, dungeon_level.height / 2)
        brush =\
            dgen.RandomTriShapedBrush(dgen.ReplaceTerrain(terrain.Floor))
        end_condition = dgen.CountDownCondition(dungeon_level.width *
                                                dungeon_level.height * 0.2)
        move_list = list(direction.DIAGONAL_DIRECTIONS)
        dgen.drunkard_walk(dungeon_level, center_position, brush,
                           end_condition, move_list)

    def tunnler(self):
        dungeon_level = self.dungeon_level
        center_position = (dungeon_level.width / 2, dungeon_level.height / 2)
        brush = dgen.SinglePointBrush(dgen.ReplaceTerrain(terrain.Floor))
        end_condition = dgen.CountDownCondition(17)
        move_list = list(direction.AXIS_DIRECTIONS)
        dgen.dfs_tunnler(dungeon_level, center_position, 4, 12, brush,
                         end_condition, move_list)

    def cellular_cave(self):
        dgen.cellular_automata(self.dungeon_level)

    def handle_input(self):
        key = inputhandler.handler.get_keypress()
        if key in inputhandler.move_controls:
            delta = inputhandler.move_controls[key]
            self.camera.camera_offset =\
                geo.add_2d(delta, self.camera.camera_offset)

        elif key == inputhandler.ESCAPE:
            self.current_stack.pop()

        elif key == inputhandler.ONE:
            self.drunkard_walk()

        elif key == inputhandler.TWO:
            self.cellular_cave()

        elif key == inputhandler.THREE:
            self.random_exlosion()

        elif key == inputhandler.FOUR:
            self.tunnler()

        elif key == inputhandler.FIVE:
            self.drunkard_walk2()

        elif key == inputhandler.SIX:
            self.generate_dungeon_level()

        elif key == inputhandler.ZERO:
            self.fill_dungeon()

        elif key == inputhandler.PRINTSCREEN:
            console.print_screen()
