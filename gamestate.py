import dungeonlevel
import player
import dungeon
import monster
import geometry as geo
import item
import gui
import camera
import constants
import rectfactory
import turn
import messenger
import state


def reset_globals():
    turn.current_turn = 0
    messenger.messenger = messenger.Messenger()


class GameStateBase(state.State):
    def __init__(self):
        reset_globals()
        self.player = player.Player(self)
        self._init_gui()
        camera_position =\
            geo.Vector2D(constants.MONSTER_STATUS_BAR_WIDTH, 0)
        self.camera = camera.Camera(camera_position, geo.zero2d())
        self.has_won = False

    def draw(self):
        dungeon_level = self.player.dungeon_level
        dungeon_level.draw(self.camera)
        self.player_status_bar.draw()
        self.message_bar.draw()
        self.monster_status_bar.draw()

    def update(self):
        if(self.player.turn_over):
            turn.current_turn += 1
        self.message_bar.update()

        dungeon_level = self.player.dungeon_level
        dungeon_level.update()

        entities = dungeon_level.entities
        self._update_entities(entities)

        self._update_gui()

        if(self.player.is_dead()):
            self.current_stack.pop()
        if(self.has_won):
            self.current_stack.pop()

    def _update_gui(self):
        self.monster_status_bar.update(self.player)
        self.player_status_bar.update()
        self.camera.update(self.player)

    def _update_entities(self, entities):
        self._entities_calculate_fov(entities)
        self._entities_act(entities)
        self._entities_equipment_effects(entities)
        self._entities_clear_status(entities)
        self._entities_effects_update(entities)

    def _entities_calculate_dungeon_map(self, entities):
        for entity in entities:
            entity.update_dungeon_map()
        self._dungeon_map_timestamp = turn.current_turn

    def _entities_calculate_fov(self, entities):
        for entity in entities:
            entity.update_fov()

    def _entities_effects_update(self, entities):
        for entity in entities:
            entity.update_effect_queue()

    def _entities_act(self, entities):
        monsters = self._get_all_non_players(entities)
        if(not player is None and not self.player.is_dead()):
            self.player.update()
        if(self.player.turn_over):
            for current_monster in monsters:
                if(not current_monster.is_dead()):
                    current_monster.update(player)

    def _get_all_non_players(self, entities):
        return [entity for entity in entities
                if(not isinstance(entity, player.Player))]

    def _entities_equipment_effects(self, entities):
        for entity in entities:
            if(not entity.is_dead()):
                entity.equipment.execute_equip_effects()

    def _entities_clear_status(self, entities):
        for entity in entities:
            entity.clear_all_status()

    def _init_gui(self):
        player_status_rect = rectfactory.player_status_rect()
        self.player_status_bar =\
            gui.PlayerStatusBar(player_status_rect,
                                self.player)

        monster_status_rect = geo.Rect(geo.zero2d(),
                                       constants.MONSTER_STATUS_BAR_WIDTH,
                                       constants.MONSTER_STATUS_BAR_HEIGHT)

        self.monster_status_bar =\
            gui.EntityStatusList(monster_status_rect,
                                 vertical_space=1)

        self.message_bar =\
            gui.MessageDisplay(rectfactory.message_display_rect())


class GameState(GameStateBase):
    def __init__(self):
        super(GameState, self).__init__()
        self.dungeon = dungeon.Dungeon(self)
        self._init_player_position()

    def _init_player_position(self):
        first_level = self.dungeon.get_dungeon_level(0)
        for stairs in first_level.up_stairs:
            move_succeded = self.player.try_move(stairs.position, first_level)
            if(move_succeded):
                return
        raise


class TestGameState(GameStateBase):
    def __init__(self):
        super(TestGameState, self).__init__()
        self.dungeon_level =\
            dungeonlevel.dungeon_level_from_file("test.level")

        self._init_player()
        self._init_items()
        self._init_monsters()

    def _init_player(self):
        start_position = geo.Vector2D(20, 10)
        player_move_success = self.player.try_move(start_position,
                                                   self.dungeon_level)
        if(not player_move_success):
            self.player.try_move(geo.Vector2D(1, 1),
                                 self.dungeon_level)

    def _init_items(self):
        gun1 = item.Gun()
        gun2 = item.Gun()
        gun1_position = geo.Vector2D(20, 20)
        gun2_position = geo.Vector2D(22, 20)

        potion = item.HealthPotion()
        potion_position = geo.Vector2D(24, 16)

        ring = item.RingOfInvisibility()
        ring_position = geo.Vector2D(20, 13)

        gun1.try_move(gun1_position, self.dungeon_level)
        gun2.try_move(gun2_position, self.dungeon_level)
        potion.try_move(potion_position, self.dungeon_level)
        ring.try_move(ring_position, self.dungeon_level)

    def _init_monsters(self):
        rat = monster.RatMan()
        rat_pos = geo.Vector2D(15, 15)
        rat.try_move(rat_pos, self.dungeon_level)

        statue = monster.StoneStatue()
        statue_pos = geo.Vector2D(25, 7)
        statue.try_move(statue_pos, self.dungeon_level)
