import equipactions
import equipment
import graphic
import inputhandler
import geometry as geo
import colors
import gui
import inventory
import menufactory


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


class Menu(gui.UIElement):
    def __init__(self, offset, state_stack,
                 margin=geo.zero2d(), vertical_space=1, may_escape=True, vi_keys_accepted=True, description_card=None):
        super(Menu, self).__init__(margin)
        self._menu_items = []
        self._state_stack = state_stack
        self._selected_index = 0
        self.offset = offset
        self._wrap = True
        self.may_escape = may_escape
        self._item_stack_panel = gui.StackPanelVertical((0, 0), vertical_space=vertical_space)
        self.vi_keys_accepted = vi_keys_accepted
        self.description_card = description_card

    @property
    def rect(self):
        return geo.Rect(self.offset, self.width, self.height)

    @property
    def width(self):
        return self._item_stack_panel.width

    @property
    def height(self):
        return self._item_stack_panel.height

    @property
    def selected_index(self):
        return self._selected_index

    @selected_index.setter
    def selected_index(self, value):
        if not value is self._selected_index and not value is None:
            self._selected_index = value
            self._signal_new_index()

    def update(self):
        self._recreate_option_list()
        if not self.has_valid_option_selected():
            self.try_set_index_to_valid_value()
        self._recreate_option_list()

        inputhandler.handler.update_keys()
        key = inputhandler.handler.get_keypress()
        if (key == inputhandler.UP or (self.vi_keys_accepted and key == inputhandler.VI_NORTH)
            or (key == inputhandler.TAB and inputhandler.handler.is_special_key_pressed(inputhandler.KEY_SHIFT))):
            self.index_decrease()
        if(key == inputhandler.DOWN or (self.vi_keys_accepted and key == inputhandler.VI_SOUTH)
           or key == inputhandler.TAB):
            self.index_increase()
        if key == inputhandler.ENTER or key == inputhandler.SPACE:
            self.activate()
        if key == inputhandler.ESCAPE and self.may_escape:
            self._state_stack.pop()

    def try_set_index_to_valid_value(self):
        if not any(menu_item.can_activate() for menu_item in self._menu_items):
            self.selected_index = None
        self.selected_index = 0
        if not self.has_valid_option_selected():
            self.index_increase()

    def has_valid_option_selected(self):
        return (0 <= self.selected_index < len(self._menu_items) and
                self._menu_items[self.selected_index].can_activate())

    def _update_menu_items(self):
        pass

    def _recreate_option_list(self):
        self._update_menu_items()
        self._item_stack_panel.clear()
        for index, item in enumerate(self._menu_items):
            if index == self.selected_index:
                menu_item = item.selected_ui_representation()
            elif item.can_activate():
                menu_item = item.unselected_ui_representation()
            else:
                menu_item = item.inactive_ui_representation()
            self._item_stack_panel.append(menu_item)

    def can_activate(self):
        return (not self.selected_index is None and
                self._menu_items[self.selected_index].can_activate())

    def activate(self):
        if self.can_activate():
            selected_option = self._menu_items[self.selected_index]
            selected_option.activate()

    def index_increase(self):
        if(not any(item.can_activate() for item in self._menu_items) or
           self.selected_index is None):
            self.selected_index = None
            return
        self._offset_index(1)
        if not self._menu_items[self.selected_index].can_activate():
            self.index_increase()

    def index_decrease(self):
        if(not any(item.can_activate() for item in self._menu_items) or
           self.selected_index is None):
            self.selected_index = None
            return
        self._offset_index(-1)
        if not self._menu_items[self.selected_index].can_activate():
            self.index_decrease()

    def _offset_index(self, offset):
        if len(self._menu_items) == 0 or self.selected_index is None:
            return
        if self._wrap:
            # Will behave strangely for when offset is less than -menu_size
            self.selected_index = (offset + self.selected_index + len(self._menu_items)) % len(self._menu_items)
        else:
            self.selected_index = clamp(offset + self.selected_index, 0, len(self._menu_items) - 1)

    def draw(self, offset=geo.zero2d()):
        real_offset = geo.int_2d(geo.add_2d(geo.add_2d(self.offset, offset),
                                            self.margin))
        self._item_stack_panel.draw(real_offset)

    def update_description(self):
        if self.description_card:
            selected_option = self._menu_items[self.selected_index]
            self.description_card.description = selected_option.description

    def _signal_new_index(self):
        self.update_description()


class MenuOption(gui.UIElement):
    def __init__(self, text, functions, can_activate=(lambda: True), description=None):
        self._functions = functions
        self.can_activate = can_activate
        self._selected = gui.TextBox(text, geo.zero2d(), colors.TEXT_SELECTED)
        self._unselected = gui.TextBox(text, geo.zero2d(), colors.TEXT_UNSELECTED)
        self._inactive = gui.TextBox(text, geo.zero2d(), colors.TEXT_INACTIVE)
        self.description = description

    def activate(self):
        for function in self._functions:
            function()
        return

    @property
    def width(self):
        return self._selected.width

    @property
    def height(self):
        return self._selected.height

    def selected_ui_representation(self):
        return self._selected

    def unselected_ui_representation(self):
        return self._unselected

    def inactive_ui_representation(self):
        return self._inactive


#TODO MenuOption should probably have a graphic representation object
# this should not be solved by subclassing!
class MenuOptionWithSymbols(MenuOption):
    def __init__(self, text, selected_graphic_char, unselected_graphic_char,
                 functions, can_activate=(lambda: True), description=None):
        super(MenuOptionWithSymbols, self).__init__(text, functions, can_activate, description=description)
        self.selected_graphic_char = selected_graphic_char
        self.unselected_graphic_char = unselected_graphic_char

        self._selected = gui.StackPanelHorizontal(geo.zero2d(), horizontal_space=1)
        self._selected.append(gui.SymbolUIElement(geo.zero2d(), self.selected_graphic_char))
        self._selected.append(gui.TextBox(text, geo.zero2d(), colors.TEXT_SELECTED))

        self._unselected = gui.StackPanelHorizontal(geo.zero2d(), horizontal_space=1)
        self._unselected.append(gui.SymbolUIElement(geo.zero2d(), self.unselected_graphic_char))
        self._unselected.append(gui.TextBox(text, geo.zero2d(), colors.TEXT_UNSELECTED))

        self._inactive = gui.StackPanelHorizontal(geo.zero2d(), horizontal_space=1)
        self._inactive.append(gui.SymbolUIElement(geo.zero2d(), self.unselected_graphic_char))
        self._inactive.append(gui.TextBox(text, geo.zero2d(), colors.TEXT_INACTIVE))


class StaticMenu(Menu):
    def __init__(self, offset, menu_items, state_stack, margin=geo.zero2d(),
                 vertical_space=1, may_escape=True, vi_keys_accepted=True):
        super(StaticMenu, self).__init__(offset, state_stack, margin=margin, vertical_space=vertical_space,
                                         may_escape=may_escape, vi_keys_accepted=vi_keys_accepted)
        self._menu_items = menu_items
        self.try_set_index_to_valid_value()
        self._recreate_option_list()


class InventoryMenu(Menu):
    def __init__(self, offset, player, state_stack, description_card,
                 margin=geo.zero2d(), vertical_space=1, may_escape=True):
        super(InventoryMenu, self).__init__(offset, state_stack, margin=margin,
                                            vertical_space=vertical_space, may_escape=may_escape,
                                            description_card=description_card)
        self._player = player
        self.try_set_index_to_valid_value()

    def _update_menu_items(self):
        item_rect = geo.Rect(self.parent.offset,
                             self.parent.width, self.parent.height)
        self._menu_items = []
        for item in self._player.inventory.get_items_sorted():
            menu_item_action = OpenItemActionMenuAction(self._state_stack, item_rect, item, self._player)
            menu_item_can_activate_function = (lambda: (len(item.get_children_with_tag("user_action")) >= 1))
            item_icon = item.graphic_char
            menu_option = MenuOptionWithSymbols(_get_item_option_text(item), item_icon, item_icon, [menu_item_action],
                                                menu_item_can_activate_function, description=item.description)
            self._menu_items.append(menu_option)
        if self.description_card.description is None:
            self.update_description()


def _get_item_option_text(item):
    if item.has_child("stacker"):
        return item.description.name + " (" + str(item.stacker.size) + ")"
    return item.description.name


class EquipmentMenu(Menu):
    def __init__(self, offset, player, state_stack, description_card,
                 margin=geo.zero2d(), may_escape=True):
        super(EquipmentMenu, self).__init__(offset, state_stack, margin=margin,
                                            may_escape=may_escape, description_card=description_card)
        self.player = player
        self.try_set_index_to_valid_value()

    def _update_menu_items(self):
        self._menu_items = []
        for slot in equipment.EquipmentSlots.ALL:
            slot_menu = menufactory.equipment_slot_menu(self.player, slot, self._state_stack)
            option_func = menufactory.DelayedStatePush(self._state_stack, slot_menu)
            item_in_slot = self.player.equipment.get(slot)
            if item_in_slot is None:
                item_name = "-"
                item_graphic = graphic.GraphicChar(None, colors.NOT_EQUIPPED_FG, slot.icon)
                description = None
            else:
                item_name = item_in_slot.description.name
                item_graphic = item_in_slot.graphic_char
                description = item_in_slot.description
            self._menu_items.append(MenuOptionWithSymbols(item_name, item_graphic, item_graphic, [option_func],
                                                          description=description))
        if self.description_card.description is None:
            self.update_description()


class EquipSlotMenu(Menu):
    def __init__(self, offset, player, equipment_slot, state_stack, description_card,
                 margin=geo.zero2d(), may_escape=True):
        super(EquipSlotMenu, self).__init__(offset, state_stack, margin=margin,
                                            may_escape=may_escape, description_card=description_card)
        self.player = player
        self.try_set_index_to_valid_value()
        self.equipment_slot = equipment_slot

    def _update_menu_items(self):
        items = self.player.inventory.items_of_equipment_type(self.equipment_slot.equipment_type)
        self._menu_items = []
        for item in items:
            reequip_function = item.reequip_action.delayed_call(source_entity=self.player, target_entity=self.player,
                                                                equipment_slot=self.equipment_slot)
            stack_pop_function = BackToGameFunction(self._state_stack)
            functions = [reequip_function, stack_pop_function]
            self._menu_items.append(MenuOptionWithSymbols(item.description.name, item.graphic_char,
                                                          item.graphic_char, functions, description=item.description))

        unequip_function = equipactions.UnequipAction().delayed_call(source_entity=self.player, target_entity=self.player,
                                                                     equipment_slot=self.equipment_slot)
        stack_pop_function = BackToGameFunction(self._state_stack)
        unequip_functions = [unequip_function, stack_pop_function]
        none_item_graphic = graphic.GraphicChar(None, colors.NOT_EQUIPPED_FG, self.equipment_slot.icon)
        self._menu_items.append(MenuOptionWithSymbols("- None -", none_item_graphic,
                                                      none_item_graphic, unequip_functions))
        if self.description_card.description is None:
            self.update_description()

        self._item_stack_panel.vertical_space = 1 if len(items) * 2 + 2 <= inventory.ITEM_CAPACITY else 0


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
                 margin=geo.zero2d(), vertical_space=1, may_escape=True):
        super(ItemActionsMenu, self).__init__(offset, state_stack,
                                              margin=margin, vertical_space=vertical_space,
                                              may_escape=True)
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
                           (lambda: item_action.can_act(source_entity=self._player,
                                                        target_entity=self._player)))
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
