import dungeongenerator as dgen
import vector2d as v2d
import camera
import turn
import constants
import messenger
import inputhandler
import state
import terrain


def reset_globals():
    turn.current_turn = 0
    messenger.messenger = messenger.Messenger()


class DungeonCreatorVisualizer(state.State):
    def __init__(self):
        super(DungeonCreatorVisualizer, self).__init__()
        self.dungeon_level = dgen.get_full_wall_dungeon(70, 55, 0)
        self.camera = camera.Camera(v2d.zero(), v2d.zero())

    def fill_dungeon(self):
        width = self.dungeon_level.width
        height = self.dungeon_level.height
        self.dungeon_level = dgen.get_full_wall_dungeon(width, height, 0)

    def draw(self):
        self.dungeon_level.draw_everything(self.camera)

    def update(self):
        self.handle_input()

    def random_exlosion(self):
        dungeon_level = self.dungeon_level
        center_position = v2d.Vector2D(dungeon_level.width / 2,
                                       dungeon_level.height / 2)
        brush = dgen.SinglePointBrush(dgen.ReplaceTerrain(terrain.Floor))
        end_condition = dgen.CountDownCondition(dungeon_level.width *
                                                dungeon_level.height * 0.2)
        move_list = list(constants.DIRECTIONS.values())
        dgen.random_exlosion(center_position, dungeon_level, brush,
                             end_condition, move_list)

    def drunkard_walk(self):
        dungeon_level = self.dungeon_level
        center_position = v2d.Vector2D(dungeon_level.width / 2,
                                       dungeon_level.height / 2)
        brush = dgen.SinglePointBrush(dgen.ReplaceTerrain(terrain.Floor))
        end_condition = dgen.CountDownCondition(dungeon_level.width *
                                                dungeon_level.height * 0.2)
        move_list = list(constants.DIRECTIONS.values())
        dgen.drunkard_walk(center_position, dungeon_level, brush,
                           end_condition, move_list)

    def cellular_cave(self):
        dgen.cellular_automata(self.dungeon_level)

    def handle_input(self):
        key = inputhandler.get_keypress()
        if key in inputhandler.move_controls:
            dx, dy = inputhandler.move_controls[key]
            self.camera.camera_offset += v2d.Vector2D(dx, dy)

        elif key == inputhandler.ESCAPE:
            self.current_stack.pop()

        elif key == inputhandler.ONE:
            self.drunkard_walk()

        elif key == inputhandler.TWO:
            self.cellular_cave()

        elif key == inputhandler.THREE:
            self.random_exlosion()

        elif key == inputhandler.ZERO:
            self.fill_dungeon()
