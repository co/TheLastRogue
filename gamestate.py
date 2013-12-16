import os
from os.path import isfile
from os import listdir, getcwd
import cPickle as pickle
import colors
from dungeon import Dungeon
from dungeonlevelfactory import dungeon_level_from_file
import libtcodpy
from mover import teleport_monsters
from player import Player
import camera
import console
import constants
import gui
import item
import menufactory
import messenger
import monster
import rectfactory
import settings
import state
import statestack
from tools import time_it
import turn


def reset_globals():
    turn.current_turn = 0
    messenger.messenger = messenger.Messenger()


class GameStateBase(state.State):
    def __init__(self, player_name=""):
        super(GameStateBase, self).__init__()
        self.dungeon = Dungeon(self)
        self.player = Player(self)
        if player_name == "":
            self.player.description.name = "Roland"
        else:
            self.player.description.name = player_name
        self._init_caches_and_flags()
        messenger.messenger.message("Welcome to: The Last Rogue!")

    def _init_caches_and_flags(self):
        """
        Sets up all variables for a new gamestate instance
        """
        reset_globals()
        self._init_gui()
        self._should_draw = True
        self._last_dungeon_level = None

        self.camera = camera.Camera((0, 0), (0, 0), self)
        self.has_won = False
        self.menu_prompt_stack = statestack.GameMenuStateStack(self)
        self.dungeon_needs_redraw = True
        self._background_console = self._console = libtcodpy.console_new(constants.GAME_STATE_WIDTH,
                                                                         constants.GAME_STATE_HEIGHT)
        self.first_round = True
        self._init_bg()

    def __getstate__(self):
        state = {
            "player": self.player,
            "dungeon": self.dungeon
        }
        return state

    def __setstate__(self, state):
        self.player = state["player"]
        self.dungeon = state["dungeon"]
        self._init_caches_and_flags()

    def _init_gui(self):
        self.entity_stack_panel = gui.StackPanelVertical((0, 0))
        self.entity_stack_panel.append(gui.EntityStatusList(self.player, constants.LEFT_SIDE_BAR_WIDTH, vertical_space=0))
        self.entity_stack_panel.append(gui.PlayerStatusBox(rectfactory.player_status_rect(), self.player))
        self.gui_dock = gui.UIDock(rectfactory.full_screen_rect())
        self.gui_dock.bottom_left = self.entity_stack_panel
        self.command_list_bar = gui.CommandListPanel(rectfactory.right_side_menu_rect())
        self.gui_dock.bottom_right = self.command_list_bar
        self._message_display = gui.MessageDisplay(rectfactory.message_display_rect())

    def _init_bg(self):
        for x in range(constants.GAME_STATE_WIDTH):
            for y in range(constants.GAME_STATE_WIDTH):
                console.console.set_colors_and_symbol((x, y), colors.UNSEEN_FG, colors.UNSEEN_BG, " ",
                                                      console=self._background_console)

    def signal_new_level(self):
        self.camera.center_on_entity(self.player)
        self.dungeon_needs_redraw = True
        if not self.first_round:
            save(self)

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
        dungeon_level = self.player.dungeon_level.value
        self._draw_bg()
        if self.dungeon_needs_redraw:
            dungeon_level.draw_all_within_screen(self.camera)
            self.dungeon_needs_redraw = False
        else:
            dungeon_level.draw_close_to_player(self.camera)
        self.player.path.draw(self.camera)
        self.prepare_draw_gui()

    def prepare_draw_gui(self):
        self._message_display.draw()
        self.gui_dock.draw()

    def update(self):
        self._message_display.update()

        dungeon_level = \
            self.player.dungeon_level.value
        if not dungeon_level is self._last_dungeon_level:
            self.signal_new_level()
        self._last_dungeon_level = dungeon_level

        self._update_gui()
        dungeon_level.tick()

        if self.player.health.is_dead():
            self.force_draw()
            game_over_screen = menufactory.game_over_screen(self.current_stack)
            delete_save_file_of_game_state()
            self.current_stack.push(game_over_screen)
        if self.has_won:
            victory_screen = menufactory.victory_screen(self.current_stack)
            delete_save_file_of_game_state()
            self.current_stack.push(victory_screen)

        self.first_round = False

    def _update_gui(self):
        self.entity_stack_panel.update()
        self.command_list_bar.update()

    def _draw_bg(self):
        libtcodpy.console_blit(self._background_console, 0, 0, constants.GAME_STATE_WIDTH, constants.GAME_STATE_HEIGHT,
                               0, 0, 0)
    def draw_loading_screen(self, text):
        libtcodpy.console_blit(self._background_console, 0, 0, constants.GAME_STATE_WIDTH, constants.GAME_STATE_HEIGHT,
                               0, 0, 0)
        console.console.print_text((settings.SCREEN_WIDTH / 2 - len(text) / 2,
                                    settings.SCREEN_HEIGHT / 2), text)
        console.console.flush()

class TestGameState(GameStateBase):
    def __init__(self, player_name=""):
        super(TestGameState, self).__init__(player_name)
        reset_globals()
        start_position = (20, 10)
        self.dungeon_level = dungeon_level_from_file("test.level")
        self.player.mover.try_move(start_position, self.dungeon_level)
        self.camera.center_on_entity(self.player)

        potion = item.HealthPotion()
        potion.mover.try_move((20, 12), self.dungeon_level)

        ring1 = item.RingOfEvasion()
        ring1.mover.try_move((24, 11), self.dungeon_level)

        ring2 = item.RingOfStealth()
        ring2.mover.try_move((25, 11), self.dungeon_level)

        ring3 = item.RingOfStrength()
        ring3.mover.try_move((26, 11), self.dungeon_level)

        device1 = item.DarknessDevice()
        device1.mover.try_move((24, 12), self.dungeon_level)

        device2 = item.HeartStopDevice()
        device2.mover.try_move((25, 12), self.dungeon_level)

        gun = item.Gun()
        gun.mover.try_move((20, 13), self.dungeon_level)

        sling = item.Sling()
        sling.mover.try_move((20, 14), self.dungeon_level)

        sword = item.Sword()
        sword.mover.try_move((19, 13), self.dungeon_level)

        armor = item.LeatherArmor()
        armor.mover.try_move((21, 10), self.dungeon_level)

        boots = item.LeatherBoots()
        boots.mover.try_move((22, 10), self.dungeon_level)

        cap = item.LeatherCap()
        cap.mover.try_move((23, 10), self.dungeon_level)

        rat = monster.Ratman(self)
        rat.mover.try_move((20, 8), self.dungeon_level)

        ghost = monster.Ghost(self)
        ghost.mover.try_move((21, 8), self.dungeon_level)

        slime = monster.Slime(self)
        slime.mover.try_move((20, 18), self.dungeon_level)

        cyclops = monster.Cyclops(self)
        cyclops.mover.try_move((2, 2), self.dungeon_level)

        jericho = monster.Jericho(self)
        jericho.mover.try_move((56, 14), self.dungeon_level)

        for i in range(5):
            ammo = item.Ammunition()
            ammo.mover.try_move((21 + i, 13), self.dungeon_level)

        for i in range(23):
            knife = item.Knife()
            knife.mover.try_move((10 + i, 23), self.dungeon_level)


class GameState(GameStateBase):
    def __init__(self, player_name=""):
        super(GameState, self).__init__(player_name)
        self.dungeon = Dungeon(self)
        self._init_player_position()

    def _init_player_position(self):
        first_level = self.dungeon.get_dungeon_level(0)
        self.dungeon_level = first_level
        for stairs in first_level.up_stairs:
            move_succeded = self.player.mover.move_push_over(stairs.position.value, first_level)
            if move_succeded:
                self.camera.center_on_entity(self.player)
                teleport_monsters(self.player)
                return
        raise Exception("Could not put player at first up stairs.")


def get_save_file_name():
    save_file = "game.sav"
    return save_file


def save(game_state):
    game_state.draw_loading_screen("Saving...")
    save_file = open(get_save_file_name(), 'wb')
    time_it("save", lambda: pickle.dump(game_state, save_file, -1))
    save_file.close()


def get_save_files():
    directory = getcwd()
    return [f for f in listdir(directory)
            if isfile(f) and f == get_save_file_name()]


def delete_save_file_of_game_state():
    file_name = get_save_file_name()
    if os.path.isfile(file_name):
        os.remove(file_name)


def is_there_a_saved_game():
    return len(get_save_files()) > 0


def load_first_game():
    save_file = open(get_save_files()[0], 'rb')
    game_state = time_it("load", (lambda: pickle.load(save_file)))
    save_file.close()
    return game_state
