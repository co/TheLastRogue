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
import turn
import gamestate


class Game(gamestate.GameState):
    def __init__(self):
        super(Game, self).__init__()
        self.dungeon_level = dungeonlevel.dungeon_level_from_file("test.level")
        camera_position =\
            vector2d.Vector2D(constants.MONSTER_STATUS_BAR_WIDTH, 0)
        self.camera = camera.Camera(camera_position, vector2d.ZERO)

        self.hero = player.Player()
        start_position = vector2d.Vector2D(20, 10)
        self.hero.try_move(start_position, self.dungeon_level)

        rat = monster.RatMan()
        rat_pos = vector2d.Vector2D(15, 15)
        rat.try_move(rat_pos, self.dungeon_level)

        statue = monster.StoneStatue()
        statue_pos = vector2d.Vector2D(25, 7)
        statue.try_move(statue_pos, self.dungeon_level)

        gun = item.Gun()
        item_position = vector2d.Vector2D(20, 20)

        gun.try_move(item_position, self.dungeon_level)

        status_bar_position = vector2d.Vector2D(settings.WINDOW_WIDTH -
                                                constants.STATUS_BAR_WIDTH, 0)
        self.status_bar =\
            gui.StackPanel(status_bar_position, constants.STATUS_BAR_WIDTH,
                           constants.STATUS_BAR_HEIGHT, colors.DB_BLACK)

        self.monster_status_bar =\
            gui.EntityStatusList(vector2d.ZERO,
                                 constants.MONSTER_STATUS_BAR_WIDTH,
                                 constants.MONSTER_STATUS_BAR_HEIGHT,
                                 colors.DB_BLACK)

        self.hp_bar = gui.CounterBar(self.hero.hp,
                                     constants.STATUS_BAR_WIDTH - 2,
                                     colors.DB_BROWN, colors.DB_LOULOU)

        self.text_box = gui.TextBox("CO\nThe Brave", vector2d.ZERO,
                                    constants.STATUS_BAR_WIDTH - 2,
                                    1, colors.DB_PANCHO)

        self.status_bar.elements.append(self.text_box)
        self.status_bar.elements.append(self.hp_bar)

        message_bar_position =\
            vector2d.Vector2D(constants.MONSTER_STATUS_BAR_WIDTH,
                              constants.LEVEL_HEIGHT)

        self.message_bar =\
            gui. MessageDisplay(message_bar_position,
                                constants.MESSAGES_BAR_WIDTH,
                                constants.MESSAGES_BAR_HEIGHT,
                                colors.DB_BLACK)

    def draw(self):
        self.status_bar.draw()
        self.message_bar.draw()
        self.dungeon_level.draw(self.hero, self.camera)
        self.monster_status_bar.draw()

    def update(self):
        self.dungeon_level.update(self.hero)
        self.monster_status_bar.update(self.hero)
        self.message_bar.update()
        if(self.hero.is_dead()):
            gamestate.game_state_stack.pop()
