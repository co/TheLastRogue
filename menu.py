import inputhandler
import dungeoncreatorvisualizer
import player
import colors
import gui
import state
import vector2d
import gamestate
import settings


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


class Menu(state.State):
    def __init__(self, position, width, height):
        super(Menu, self).__init__()
        self._menu_items = []
        self._selected_index = 0
        self._wrap = True
        self.position = position
        self.width = width
        self.height = height
        self.may_escape = True
        self._item_stack_panel = gui.StackPanelVertical(vector2d.zero(),
                                                        self.width,
                                                        colors.INTERFACE_BG,
                                                        vertical_space=1)

    def update(self):
        self._recreate_option_list()
        if(not self.has_valid_option_selected()):
            self.try_set_index_to_valid_value()

        key = inputhandler.get_keypress()
        if key == inputhandler.UP:
            self.index_decrease()
        if key == inputhandler.DOWN:
            self.index_increase()
        if key == inputhandler.ENTER:
            self.activate()
        if key == inputhandler.ESCAPE and self.may_escape:
            self.current_stack.pop()

    def try_set_index_to_valid_value(self):
        if(not any(menu_item.can_activate for menu_item in self._menu_items)):
            self._selected_index = None
        self._selected_index = 0
        if(not self.has_valid_option_selected()):
            self.index_increase()

    def has_valid_option_selected(self):
        return (0 <= self._selected_index < len(self._menu_items) and
                self._menu_items[self._selected_index].can_activate)

    def _update_menu_items(self):
        pass

    def _recreate_option_list(self):
        self._update_menu_items()
        self._item_stack_panel.elements = []
        for index, item in enumerate(self._menu_items):
            if(index == self._selected_index):
                color = colors.TEXT_SELECTED
            elif(item.can_activate):
                color = colors.TEXT_UNSELECTED
            else:
                color = colors.TEXT_INACTIVE
            menu_item = gui.TextBox(item.text, vector2d.zero(), color)
            self._item_stack_panel.elements.append(menu_item)

    def can_activate(self):
        return not self._selected_index is None

    def activate(self):
        if(self.can_activate()):
            selected_option = self._menu_items[self._selected_index]
            selected_option.activate()

    def index_increase(self):
        if(not any(item.can_activate for item in self._menu_items) or
           self._selected_index is None):
            return
        self._offset_index(1)
        if(not self._menu_items[self._selected_index].can_activate):
            self.index_increase()

    def index_decrease(self):
        if(not any(item.can_activate for item in self._menu_items) or
           self._selected_index is None):
            return
        self._offset_index(-1)
        if(not self._menu_items[self._selected_index].can_activate):
            self.index_decrease()

    def _offset_index(self, offset):
        if(len(self._menu_items) == 0 or self._selected_index is None):
            return
        if(self._wrap):
            # Will behave strangely for when offset is less than -menu_size
            self._selected_index =\
                (offset + self._selected_index + len(self._menu_items))\
                % len(self._menu_items)
        else:
            self._selected_index = clamp(offset + self._selected_index, 0,
                                         len(self._menu_items) - 1)

    def draw(self):
        self._item_stack_panel.draw(self.position)


class MenuOption(object):
    def __init__(self, text, activate_function,
                 can_activate=True):
        self.text = text
        self._activate_function = activate_function
        self.can_activate = can_activate

    def activate(self):
        return self._activate_function()


class MainMenu(Menu):
    def __init__(self, position, width, height):
        super(MainMenu, self).__init__(position, width, height)
        start_test_game_function =\
            lambda: self.current_stack.push(gamestate.TestGameState())
        start_game_function =\
            lambda: self.current_stack.push(gamestate.GameState())
        quit_game_function = lambda: self.current_stack.pop()
        dungeon_visualizer_function =\
            lambda: self.current_stack.push(dungeoncreatorvisualizer.
                                            DungeonCreatorVisualizer())
        start_test_game_option = MenuOption("Start Test Dungeon",
                                            start_test_game_function)
        start_game_option = MenuOption("Start Dungeon",
                                       start_game_function)
        dungeon_creator_option = MenuOption("Dungeon Creator",
                                            dungeon_visualizer_function)
        quit_option = MenuOption("Quit", quit_game_function)
        self._menu_items = [start_test_game_option, start_game_option,
                            dungeon_creator_option, quit_option]
        self._rectangle_bg = gui.Rectangle(vector2d.zero(), width,
                                           height, colors.INTERFACE_BG)

    def draw(self):
        self._rectangle_bg.draw()
        draw_position = vector2d.Vector2D(0, settings.WINDOW_HEIGHT - 7)
        self._item_stack_panel.draw(draw_position)


class InventoryMenu(Menu):
    def __init__(self, position, width, height, player):
        super(InventoryMenu, self).__init__(position,
                                            width, height)
        self._player = player
        self._rectangle_bg = gui.Rectangle(vector2d.zero(), width,
                                           height, colors.INTERFACE_BG)
        self.rectangle_screen_grey =\
            gui.RectangleGray(vector2d.zero(),
                              settings.WINDOW_WIDTH,
                              settings.WINDOW_HEIGHT,
                              colors.DB_OPAL)
        heading = gui.TextBox("Inventory:", vector2d.zero(),
                              colors.INVENTORY_HEADING,
                              margin=vector2d.Vector2D(0, 1))
        self._inventory_stack_panel =\
            gui.StackPanelVertical(vector2d.zero(),
                                   width,
                                   colors.INTERFACE_BG)
        self._inventory_stack_panel.elements.append(heading)
        self._inventory_stack_panel.elements.append(self._item_stack_panel)
        self._update_menu_items()
        self.try_set_index_to_valid_value()

    def activate(self):
        if(self.can_activate()):
            selected_option = self._menu_items[self._selected_index]
            selected_option.activate()

    @staticmethod
    def can_open_item_action_menu(item):
        if(len(item.actions) >= 1):  # No actions no need for menu.
            return True
        return False

    def open_item_action_menu(self, item, position, width, height, player):
        item_actions_menu = ItemActionsMenu(position, width,
                                            height, item,
                                            player)
        self.current_stack.push(item_actions_menu)

    def _update_menu_items(self):
        self._menu_items =\
            [MenuOption(item.name,
                        OpenItemActionMenu(self.current_stack,
                                           self.position, self.width,
                                           self.height, item,
                                           self._player),
                        (len(item.actions) >= 1))
             for item in self._player.inventory.items]

    def draw(self):
        self.rectangle_screen_grey.draw(vector2d.zero())
        self._rectangle_bg.draw(self.position)
        self._inventory_stack_panel.draw(self.position)


class OpenItemActionMenu():
    def __init__(self, state_stack, position, width, height, item, player):
        self.position = position
        self.width = width
        self.height = height
        self._item = item
        self._player = player
        self._state_stack = state_stack

    def __call__(self):
        item_actions_menu = ItemActionsMenu(self.position, self.width,
                                            self.height, self._item,
                                            self._player)
        self._state_stack.push(item_actions_menu)


class ItemActionsMenu(Menu):
    def __init__(self, position, width, height, item, player):
        super(ItemActionsMenu, self).__init__(position, width, height)
        self._menu_items = [action.name for action in item.actions]
        self._rectangle_bg = gui.Rectangle(vector2d.zero(), width,
                                           height, colors.INTERFACE_BG)
        self._actions =\
            sorted(item.actions, key=lambda action: action.display_order)
        self._player = player
        self._update_menu_items()
        self.try_set_index_to_valid_value()

    def draw(self):
        self._rectangle_bg.draw(self.position)
        self._item_stack_panel.draw(self.position)

    def _update_menu_items(self):
        self._menu_items =\
            [MenuOption(action.name,
                        DelayedAction(self.current_stack, action,
                                      self._player, self._player),
                        action.can_act(source_entity=self._player,
                                       target_entity=self._player))
             for action in self._actions]


class DelayedAction(object):
    def __init__(self, state_stack, action, source_entity, target_entity):
        self.action = action
        self.source_entity = source_entity
        self.target_entity = target_entity
        self._state_stack = state_stack

    def __call__(self):
        self.action.act(source_entity=self.source_entity,
                        target_entity=self.target_entity,
                        game_state=self._state_stack.get_game_state())
        if(isinstance(self.source_entity, player.Player)):
            self.source_entity.turn_over = True
        self._state_stack.pop()
        self._state_stack.pop()
