import dungeonlevel
import player
import monster
import vector2d
import item
import gui
import camera
import settings
import constants
import colors
import gamestate
import turn
import messenger


def reset_globals():
    turn.current_turn = 0
    messenger.messenger = messenger.Messenger()


class Game(gamestate.GameState):
    def __init__(self):
        super(Game, self).__init__()
        self.dungeon_level = dungeonlevel.dungeon_level_from_file("test.level")
        camera_position =\
            vector2d.Vector2D(constants.MONSTER_STATUS_BAR_WIDTH, 0)
        self.camera = camera.Camera(camera_position, vector2d.ZERO)

        self.player = player.Player()
        start_position = vector2d.Vector2D(20, 10)
        self.player.try_move(start_position, self.dungeon_level)

        rat = monster.RatMan()
        rat_pos = vector2d.Vector2D(15, 15)
        rat.try_move(rat_pos, self.dungeon_level)

        statue = monster.StoneStatue()
        statue_pos = vector2d.Vector2D(25, 7)
        statue.try_move(statue_pos, self.dungeon_level)

        gun = item.Gun()
        gun_position = vector2d.Vector2D(20, 20)

        potion = item.HealthPotion()
        potion_position = vector2d.Vector2D(24, 16)

        ring = item.RingOfInvisibility()
        ring_position = vector2d.Vector2D(20, 13)

        gun.try_move(gun_position, self.dungeon_level)
        potion.try_move(potion_position, self.dungeon_level)
        ring.try_move(ring_position, self.dungeon_level)

        status_bar_position = vector2d.Vector2D(settings.WINDOW_WIDTH -
                                                constants.STATUS_BAR_WIDTH, 0)
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
                              constants.LEVEL_HEIGHT)

        self.message_bar =\
            gui.MessageDisplay(message_bar_position,
                               constants.MESSAGES_BAR_WIDTH,
                               constants.MESSAGES_BAR_HEIGHT,
                               colors.INTERFACE_BG)
        reset_globals()

    def draw(self):
        self.player_status_bar.draw()
        self.message_bar.draw()
        self.dungeon_level.draw(self.camera)
        self.monster_status_bar.draw()

    def update(self):
        self.dungeon_level.update()
        self.monster_status_bar.update(self.player)
        self.player_status_bar.update()
        if(self.player.turn_over):
            turn.current_turn += 1
        self.message_bar.update()
        if(self.player.is_dead()):
            gamestate.game_state_stack.pop()
