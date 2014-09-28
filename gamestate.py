import os
from os.path import isfile
from os import listdir, getcwd
import cPickle as pickle
from cloud import new_steam_cloud
import colors
from dungeon import Dungeon, ReflexiveDungeon
import dungeonfeature
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
import sacrifice
import settings
import state
import statestack
from tools import time_it
import turn


def reset_globals(player):
    turn.current_turn = 0
    messenger.msg.clear()
    messenger.msg.player = player


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
        messenger.msg.send_global_message("Welcome to The Last Rogue!")

    def _init_caches_and_flags(self):
        """
        Sets up all variables for a new gamestate instance
        """
        reset_globals(self.player)
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

        self._gui_last_update_timestamp = -1

        self.power_list = sacrifice.new_power_list()

    def __getstate__(self):
        state = {
            "player": self.player,
            "dungeon": self.dungeon
        }
        print "get gs"
        return state

    def __setstate__(self, state):
        print "*****gamestate ", state.__class__
        print "set gs"
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
        self._message_display = gui.MessageDisplay(rectfactory.message_display_rect(), vertical_space=0)

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
        if self._gui_last_update_timestamp < turn.current_turn:
            self._update_gui()
        self._message_display.draw()
        self.gui_dock.draw()

    def update(self):
        self._message_display.update()

        dungeon_level = \
            self.player.dungeon_level.value
        if not dungeon_level is self._last_dungeon_level:
            self.signal_new_level()
        self._last_dungeon_level = dungeon_level

        #self._update_gui()
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
        self._gui_last_update_timestamp = turn.current_turn

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
        reset_globals(self.player)
        start_position = (20, 10)
        self.dungeon_level = dungeon_level_from_file("test.level")
        self.dungeon = ReflexiveDungeon(self.dungeon_level)
        self.player.mover.try_move(start_position, self.dungeon_level)
        self.camera.center_on_entity(self.player)

        cloud = new_steam_cloud(self, 32)
        cloud.mover.try_move((16, 10), self.dungeon_level)

        demon = monster.new_dust_demon(self)
        demon.mover.try_move((30, 16), self.dungeon_level)

        #ratman_mystic = monster.new_ratman_mystic(self)
        #ratman_mystic.mover.try_move((25, 16), self.dungeon_level)

        #amoeba = monster.new_giant_amoeba(self)
        #amoeba.mover.try_move((26, 14), self.dungeon_level)

        for i in range(5):
            bomb = item.new_bomb(self)
            bomb.mover.try_move((18, 12 + i), self.dungeon_level)

        potion = item.new_poison_potion(self)
        potion.mover.try_move((20, 12), self.dungeon_level)

        potion = item.new_health_potion(self)
        potion.mover.try_move((20, 16), self.dungeon_level)

        orb = item.new_flame_orb(self)
        orb.mover.try_move((22, 15), self.dungeon_level)

        amulet = item.new_amulet_of_life_steal(self)
        amulet.mover.try_move((20, 14), self.dungeon_level)

        amulet = item.new_amulet_of_reflect_damage(self)
        amulet.mover.try_move((24, 11), self.dungeon_level)

        ring2 = item.new_ring_of_stealth(self)
        ring2.mover.try_move((25, 11), self.dungeon_level)

        ring3 = item.new_ring_of_strength(self)
        ring3.mover.try_move((26, 11), self.dungeon_level)

        device1 = item.new_swap_device(self)
        device1.mover.try_move((24, 12), self.dungeon_level)

        device2 = item.new_heart_stop_device(self)
        device2.mover.try_move((25, 12), self.dungeon_level)

        scroll = item.new_teleport_scroll(self)
        scroll.mover.try_move((26, 12), self.dungeon_level)

        scroll = item.new_map_scroll(self)
        scroll.mover.try_move((21, 13), self.dungeon_level)

        gun = item.new_gun(self)
        gun.mover.try_move((20, 13), self.dungeon_level)

        sling = item.new_sling(self)
        sling.mover.try_move((20, 14), self.dungeon_level)

        mace = item.new_mace(self)
        mace.mover.try_move((19, 13), self.dungeon_level)

        blood_fountain = dungeonfeature.new_blood_fountain()
        blood_fountain.mover.try_move((21, 10), self.dungeon_level)

        charge = item.new_energy_sphere(self)
        charge.mover.try_move((22, 10), self.dungeon_level)

        cap = item.new_leather_cap(self)
        cap.mover.try_move((23, 10), self.dungeon_level)

        #pixie = monster.new_pixie(self)
        #pixie.mover.try_move((20, 14), self.dungeon_level)

        #salamander = monster.new_salamander(self)
        #salamander.mover.try_move((25, 10), self.dungeon_level)

        #slime = monster.new_slime(self)
        #slime.mover.try_move((25, 12), self.dungeon_level)

        #        spider = monster.new_spider(self)
        #        spider.mover.try_move((26, 12), self.dungeon_level)
        #
        #ghost = monster.new_ghost(self)
        #ghost.mover.try_move((21, 8), self.dungeon_level)
        #
        #        pixie = monster.new_pixie(self)
        #        pixie.mover.try_move((23, 8), self.dungeon_level)
        #
        #slime = monster.new_slime(self)
        #slime.mover.try_move((18, 16), self.dungeon_level)

        #dark_slime = monster.new_dark_slime(self)
        #dark_slime.mover.try_move((24, 18), self.dungeon_level)

        #cyclops = monster.new_cyclops(self)
        #cyclops.mover.try_move((2, 2), self.dungeon_level)

        #jericho = monster.new_jericho(self)
        #jericho.mover.try_move((56, 14), self.dungeon_level)

        for i in range(5):
            ammo = item.new_ammunition(self)
            ammo.mover.try_move((21 + i, 13), self.dungeon_level)

        for i in range(23):
            knife = item.new_knife(self)
            knife.mover.try_move((10 + i, 23), self.dungeon_level)


class GameState(GameStateBase):
    def __init__(self, player_name=""):
        super(GameState, self).__init__(player_name)
        self.dungeon = Dungeon(self)
        self._init_player_position()

    def _init_player_position(self):
        first_level = self.dungeon.get_dungeon_level(1)
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
    print save_file
    game_state = time_it("load", (lambda: pickle.load(save_file)))
    save_file.close()
    return game_state
