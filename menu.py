import inputhandler
import geometry as geo
import colors
import gui
import menufactory


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


class Menu(gui.UIElement):
    def __init__(self, offset, state_stack,
                 margin=geo.zero2d(), vertical_space=1):
        super(Menu, self).__init__(margin)
        self._menu_items = []
        self._state_stack = state_stack
        self._selected_index = 0
        self.offset = offset
        self._wrap = True
        self.may_escape = True
        self._item_stack_panel =\
            gui.StackPanelVertical(geo.zero2d(), vertical_space=vertical_space)

    @property
    def rect(self):
        return geo.Rect(self.offset, self.width, self.height)

    @property
    def width(self):
        return self._item_stack_panel.width

    @property
    def height(self):
        return self._item_stack_panel.height

    def update(self):
        self._recreate_option_list()
        if(not self.has_valid_option_selected()):
            self.try_set_index_to_valid_value()
        self._recreate_option_list()

        inputhandler.handler.update_keys()
        key = inputhandler.handler.get_keypress()
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
                menu_item = item.selected_ui_representation()
            elif(item.can_activate):
                menu_item = item.unselected_ui_representation()
            else:
                menu_item = item.inactive_ui_representation()
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
        real_offset = geo.int_2d(geo.add_2d(geo.add_2d(self.offset, offset),
                                            self.margin))
        self._item_stack_panel.draw(real_offset)


class MenuOption(gui.UIElement):
    def __init__(self, text, functions, can_activate=True):
        self.text = text
        self._functions = functions
        self.can_activate = can_activate

    def activate(self):
        for function in self._functions:
            function()
        return

    def selected_ui_representation(self):
        return gui.TextBox(self.text, geo.zero2d(), colors.TEXT_SELECTED)

    def unselected_ui_representation(self):
        return gui.TextBox(self.text, geo.zero2d(), colors.TEXT_UNSELECTED)

    def inactive_ui_representation(self):
        return gui.TextBox(self.text, geo.zero2d(), colors.TEXT_INACTIVE)


#TODO MenuOption should probably have a graphic represtation object
# this should not be solved by subclassing!
class MenuOptionWithSymbols(MenuOption):
    def __init__(self, text, selected_symbol, unselected_symbol,
                 functions, can_activate=True):
        super(MenuOptionWithSymbols, self).__init__(text, functions,
                                                    can_activate)
        self.selected_symbol = selected_symbol
        self.unselected_symbol = unselected_symbol

    def selected_ui_representation(self):
        horizontal_stack = gui.StackPanelHorizontal(geo.zero2d(),
                                                    horizontal_space=1)
        horizontal_stack.append(gui.SymbolUIElement(geo.zero2d(),
                                                    self.selected_symbol,
                                                    colors.TEXT_SELECTED))
        horizontal_stack.append(gui.TextBox(self.text, geo.zero2d(),
                                            colors.TEXT_SELECTED))
        return horizontal_stack

    def unselected_ui_representation(self):
        horizontal_stack = gui.StackPanelHorizontal(geo.zero2d(),
                                                    horizontal_space=1)
        horizontal_stack.append(gui.SymbolUIElement(geo.zero2d(),
                                                    self.unselected_symbol,
                                                    colors.TEXT_UNSELECTED))
        horizontal_stack.append(gui.TextBox(self.text, geo.zero2d(),
                                            colors.TEXT_UNSELECTED))
        return horizontal_stack

    def inactive_ui_representation(self):
        horizontal_stack = gui.StackPanelHorizontal(geo.zero2d(),
                                                    horizontal_space=1)
        horizontal_stack.append(gui.SymbolUIElement(geo.zero2d(),
                                                    self.unselected_symbol,
                                                    colors.TEXT_INACTIVE))
        horizontal_stack.append(gui.TextBox(self.text, geo.zero2d(),
                                            colors.TEXT_INACTIVE))
        return horizontal_stack


class StaticMenu(Menu):
    def __init__(self, offset, menu_items, state_stack,
                 margin=geo.zero2d(), vertical_space=1):
        super(StaticMenu, self).__init__(offset, state_stack, margin=margin,
                                         vertical_space=vertical_space)
        self._menu_items = menu_items
        self.try_set_index_to_valid_value()
        self._recreate_option_list()


class InventoryMenu(Menu):
    def __init__(self, offset, player, state_stack,
                 margin=geo.zero2d(), vertical_space=1):
        super(InventoryMenu, self).__init__(offset, state_stack, margin=margin,
                                            vertical_space=vertical_space)
        self._player = player
        self.try_set_index_to_valid_value()

    def _update_menu_items(self):
        item_rect = geo.Rect(self.parent.offset,
                             self.parent.width, self.parent.height)
        self._menu_items =\
            [MenuOption(self._get_item_option_text(item),
                        [OpenItemActionMenuAction(self._state_stack,
                                                  item_rect, item,
                                                  self._player)],
                        (len(item.get_children_with_tag("user_action")) >= 1))
             for item in self._player.inventory.get_items_sorted()]

    def _get_item_option_text(self, item):
        if(item.has_child("stacker")):
            return item.description.name + " (" + str(item.stacker.size) + ")"
        return item.description.name


class OpenItemActionMenuAction(object):
    def __init__(self, state_stack, rect, item, player):
        self.rect = rect
        self._item = item
        self._player = player
        self._state_stack = state_stack

    def __call__(self):
        item_actions_menu = menufactory.item_actions_menu(self._item,
                                                          self._player,
                                                          self._state_stack)
        self._state_stack.push(item_actions_menu)


class ItemActionsMenu(Menu):
    def __init__(self, offset, item, player, state_stack,
                 margin=geo.zero2d(), vertical_space=1):
        super(ItemActionsMenu, self).__init__(offset, state_stack,
                                              margin=margin,
                                              vertical_space=vertical_space)
        self._actions =\
            sorted(item.get_children_with_tag("user_action"),
                   key=lambda action: action.display_order)
        self._player = player
        self._update_menu_items()
        self.try_set_index_to_valid_value()

    def _update_menu_items(self):
        game_state = self._state_stack.get_game_state()
        self._menu_items = []
        for item_action in self._actions:
            action_function =\
                item_action.delayed_call(source_entity=self._player,
                                         target_entity=self._player,
                                         game_state=game_state)
            back_to_game_function = BackToGameFunction(self._state_stack)
            functions = [action_function, back_to_game_function]
            option =\
                MenuOption(item_action.name, functions,
                           item_action.can_act(source_entity=self._player,
                                               target_entity=self._player))
            self._menu_items.append(option)


class StackPopFunction(object):
    def __init__(self, state_stack, states_to_pop):
        self._state_stack = state_stack
        self._states_to_pop = states_to_pop

    def __call__(self):
        for _ in range(self._states_to_pop):
            self._state_stack.pop()


class BackToGameFunction(object):
    def __init__(self, state_stack):
        self._state_stack = state_stack

    def __call__(self):
        self._state_stack.pop_to_game_state()
