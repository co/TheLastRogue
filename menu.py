import inputhandler
import geometry as geo
import colors
import gui


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


class Menu(gui.UIElement):
    def __init__(self, rect, state_stack,
                 margin=geo.zero2d(), vertical_space=1):
        super(Menu, self).__init__(margin)
        self._menu_items = []
        self._state_stack = state_stack
        self._selected_index = 0
        self._wrap = True
        self.rect = rect
        self.may_escape = True
        self._item_stack_panel =\
            gui.StackPanelVertical(geo.zero2d(), self.width,
                                   colors.INTERFACE_BG,
                                   vertical_space=vertical_space)

    @property
    def position(self):
        return self.rect.top_left

    @property
    def width(self):
        return self.rect.width

    @property
    def height(self):
        return self.rect.height

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
            self._state_stack.pop()

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
        self._item_stack_panel.clear()
        for index, item in enumerate(self._menu_items):
            if(index == self._selected_index):
                color = colors.TEXT_SELECTED
            elif(item.can_activate):
                color = colors.TEXT_UNSELECTED
            else:
                color = colors.TEXT_INACTIVE
            menu_item = gui.TextBox(item.text, geo.zero2d(), color)
            self._item_stack_panel.append(menu_item)

    def can_activate(self):
        return (not self._selected_index is None and
                self._menu_items[self._selected_index].can_activate)

    def activate(self):
        if(self.can_activate()):
            selected_option = self._menu_items[self._selected_index]
            selected_option.activate()

    def index_increase(self):
        if(not any(item.can_activate for item in self._menu_items) or
           self._selected_index is None):
            self._selected_index = None
            return
        self._offset_index(1)
        if(not self._menu_items[self._selected_index].can_activate):
            self.index_increase()

    def index_decrease(self):
        if(not any(item.can_activate for item in self._menu_items) or
           self._selected_index is None):
            self._selected_index = None
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

    def draw(self, offset=geo.zero2d()):
        self._item_stack_panel.draw(self.position + offset)


class MenuOption(gui.UIElement):
    def __init__(self, text, activate_function,
                 can_activate=True):
        self.text = text
        self._activate_function = activate_function
        self.can_activate = can_activate

    def activate(self):
        return self._activate_function()


class StaticMenu(Menu):
    def __init__(self, rect, menu_items, state_stack,
                 margin=geo.zero2d(), vertical_space=1):
        super(StaticMenu, self).__init__(rect, state_stack)
        self._menu_items = menu_items
        self.try_set_index_to_valid_value()


class InventoryMenu(Menu):
    def __init__(self, rect, player, state_stack):
        super(InventoryMenu, self).__init__(rect, state_stack)
        self._player = player
        self.try_set_index_to_valid_value()

    def _update_menu_items(self):
        item_rect = geo.Rect(self.parent.offset,
                             self.parent.width, self.parent.height)
        self._menu_items =\
            [MenuOption(item.name,
                        OpenItemActionMenuAction(self._state_stack,
                                                 item_rect, item,
                                                 self._player),
                        (len(item.actions) >= 1))
             for item in self._player.inventory.items]


class OpenItemActionMenuAction(object):
    def __init__(self, state_stack, rect, item, player):
        self.rect = rect
        self._item = item
        self._player = player
        self._state_stack = state_stack

    def __call__(self):
        item_actions_menu = ItemActionsMenu(self.rect, self._item,
                                            self._player, self._state_stack)
        self._state_stack.push(item_actions_menu)


class ItemActionsMenu(Menu):
    def __init__(self, rect, item, player, state_stack):
        super(ItemActionsMenu, self).__init__(rect, state_stack)
        self._actions =\
            sorted(item.actions, key=lambda action: action.display_order)
        self._player = player
        self._update_menu_items()
        self.try_set_index_to_valid_value()

    def _update_menu_items(self):
        self._menu_items =\
            [MenuOption(action.name,
                        DelayedAction(self._state_stack, action,
                                      self._player, self._player,
                                      states_to_pop=2, end_player_turn=True),
                        action.can_act(source_entity=self._player,
                                       target_entity=self._player))
             for action in self._actions]


class DelayedAction(object):
    def __init__(self, state_stack, action, source_entity,
                 target_entity, states_to_pop=0, end_player_turn=True):
        self.action = action
        self.source_entity = source_entity
        self.target_entity = target_entity
        self._state_stack = state_stack
        self._states_to_pop = states_to_pop
        self._end_player_turn = end_player_turn

    def __call__(self):
        self.action.act(source_entity=self.source_entity,
                        target_entity=self.target_entity,
                        game_state=self._state_stack.get_game_state())
        if(self._end_player_turn):
            self.source_entity.turn_over = True
        for _ in range(self._states_to_pop):
            self._state_stack.pop()
