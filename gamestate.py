import dungeonlevel
import player
import monster
import vector2d
import item
import gui
import camera
import constants
import colors
import turn
import messenger
import state


def reset_globals():
    turn.current_turn = 0
    messenger.messenger = messenger.Messenger()


class GameState(state.State):
    def __init__(self):
        super(GameState, self).__init__()
        self.dungeon_level =\
            dungeonlevel.dungeon_level_from_file("big.level")
        camera_position =\
            vector2d.Vector2D(constants.MONSTER_STATUS_BAR_WIDTH, 0)
        self.camera = camera.Camera(camera_position, vector2d.ZERO)

        self.player = player.Player(self)
        start_position = vector2d.Vector2D(20, 10)
        player_move_success = self.player.try_move(start_position,
                                                   self.dungeon_level)
        if(not player_move_success):
            self.player.try_move(vector2d.Vector2D(1, 1),
                                 self.dungeon_level)

        rat = monster.RatMan()
        rat_pos = vector2d.Vector2D(15, 15)
        rat.try_move(rat_pos, self.dungeon_level)

        statue = monster.StoneStatue()
        statue_pos = vector2d.Vector2D(25, 7)
        statue.try_move(statue_pos, self.dungeon_level)

        gun1 = item.Gun()
        gun2 = item.Gun()
        gun1_position = vector2d.Vector2D(20, 20)
        gun2_position = vector2d.Vector2D(22, 20)

        potion = item.HealthPotion()
        potion_position = vector2d.Vector2D(24, 16)

        ring = item.RingOfInvisibility()
        ring_position = vector2d.Vector2D(20, 13)

        gun1.try_move(gun1_position, self.dungeon_level)
        gun2.try_move(gun2_position, self.dungeon_level)
        potion.try_move(potion_position, self.dungeon_level)
        ring.try_move(ring_position, self.dungeon_level)

        status_bar_position =\
            vector2d.Vector2D(constants.MONSTER_STATUS_BAR_WIDTH +
                              constants.GAME_STATE_WIDTH, 0)

        self.player_status_bar =\
            gui.PlayerStatusBar(status_bar_position,
                                constants.STATUS_BAR_WIDTH,
                                constants.STATUS_BAR_HEIGHT,
                                colors.INTERFACE_BG,
                                self.player,
                                margin=vector2d.Vector2D(0, 1))

        self.monster_status_bar =\
            gui.EntityStatusList(vector2d.ZERO,
                                 constants.MONSTER_STATUS_BAR_WIDTH,
                                 constants.MONSTER_STATUS_BAR_HEIGHT,
                                 colors.INTERFACE_BG,
                                 margin=vector2d.Vector2D(0, 1),
                                 vertical_space=1)

        message_bar_position =\
            vector2d.Vector2D(constants.MONSTER_STATUS_BAR_WIDTH,
                              constants.GAME_STATE_HEIGHT)

        self.message_bar =\
            gui.MessageDisplay(message_bar_position,
                               constants.MESSAGES_BAR_WIDTH,
                               constants.MESSAGES_BAR_HEIGHT,
                               colors.INTERFACE_BG)
        reset_globals()

    def draw(self):
        self.dungeon_level.draw(self.camera)
        self.player_status_bar.draw()
        self.message_bar.draw()
        self.monster_status_bar.draw()

    def update(self):
        if(self.player.turn_over):
            turn.current_turn += 1
        self.message_bar.update()
        self.dungeon_level.update()
        self.monster_status_bar.update(self.player)
        self.player_status_bar.update()
        self.camera.update(self.player)
        if(self.player.is_dead()):
            self.current_stack.pop()
