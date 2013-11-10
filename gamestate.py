from dungeon import Dungeon
from dungeonlevelfactory import dungeon_level_from_file
from player import Player
import camera
import console
import constants
import geometry as geo
import gui
import item
import menufactory
import messenger
import monster
import rectfactory
import state
import statestack
import turn


def reset_globals():
    turn.current_turn = 0
    messenger.messenger = messenger.Messenger()


class GameStateBase(state.State):
    def __init__(self):
        super(GameStateBase, self).__init__()
        reset_globals()
        self.player = Player(self)
        self._init_gui()

        self.camera = camera.Camera((0, 0), (0, 0))
        self.has_won = False
        self._should_draw = True
        self.menu_prompt_stack = statestack.GameMenuStateStack(self)
        messenger.messenger.message("Welcome to: The Last Rogue!")

    def start_prompt(self, prompt_state):
        self.menu_prompt_stack.push(prompt_state)
        self.menu_prompt_stack.main_loop()

    def signal_should_redraw_screen(self):
        self._should_draw = True

    # most of the time the drawing is handled in EntityScheduler,
    # right before the player acts.
    # if a redraw is needed do a force_draw instead.
    def draw(self):
        pass

    def force_draw(self):
        self.camera.update(self.player)
        self.prepare_draw()
        self._should_draw = False
        console.console.flush()

    def prepare_draw(self):
        dungeon_level =\
            self.player.dungeon_level.value
        dungeon_level.draw(self.camera)
        self.player_status_bar.draw()
        self.message_bar.draw()
        self.monster_status_bar.draw()

    def update(self):
        self.message_bar.update()

        dungeon_level =\
            self.player.dungeon_level.value
        dungeon_level.tick()

        self._update_gui()

        if self.player.health.is_dead():
            game_over_screen = menufactory.game_over_screen(self.current_stack)
            self.current_stack.push(game_over_screen)
        if self.has_won:
            victory_screen = menufactory.victory_screen(self.current_stack)
            self.current_stack.push(victory_screen)

    def _update_gui(self):
        self.monster_status_bar.update(self.player)
        self.player_status_bar.update()

    def _init_gui(self):
        player_status_rect = rectfactory.player_status_rect()
        self.player_status_bar =\
            gui.PlayerStatusBox(player_status_rect, self.player)

        monster_status_rect = geo.Rect(geo.zero2d(),
                                       constants.MONSTER_STATUS_BAR_WIDTH,
                                       constants.MONSTER_STATUS_BAR_HEIGHT)

        self.monster_status_bar = gui.EntityStatusList(monster_status_rect,
                                                       vertical_space=0)

        self.message_bar = gui.MessageDisplay(rectfactory.message_display_rect())


class TestGameState(GameStateBase):
    def __init__(self):
        super(TestGameState, self).__init__()
        reset_globals()
        start_position = (20, 10)
        self.dungeon_level = dungeon_level_from_file("test.level")
        self.player.mover.try_move(start_position, self.dungeon_level)

        potion = item.HealthPotion()
        potion.mover.try_move((20, 12), self.dungeon_level)

        gun = item.Gun()
        gun.mover.try_move((20, 13), self.dungeon_level)
        sword = item.Sword()
        sword.mover.try_move((19, 13), self.dungeon_level)
        armor = item.Armor()
        armor.mover.try_move((21, 10), self.dungeon_level)

        rat = monster.Ratman(self)
        rat.mover.try_move((20, 8), self.dungeon_level)

        slime = monster.Slime(self)
        slime.mover.try_move((20, 18), self.dungeon_level)

        jerico = monster.Jerico(self)
        jerico.mover.try_move((56, 14), self.dungeon_level)

        for i in range(5):
            ammo = item.Ammunition()
            ammo.mover.try_move((21 + i, 13), self.dungeon_level)

        for i in range(10):
            sword = item.Sword()
            sword.mover.try_move((21 + i, 23), self.dungeon_level)

class GameState(GameStateBase):
    def __init__(self):
        super(GameState, self).__init__()
        self.dungeon = Dungeon(self)
        self._init_player_position()

    def _init_player_position(self):
        first_level = self.dungeon.get_dungeon_level(0)
        self.dungeon_level = first_level
        for stairs in first_level.up_stairs:
            move_succeded = self.player.mover.try_move(stairs.position.value,
                                                       first_level)
            if(move_succeded):
                return
        raise Exception("Could not put player at first up stairs.")
