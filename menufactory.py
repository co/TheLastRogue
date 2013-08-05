import gamestate
import equipment
import rectfactory
import dungeoncreatorvisualizer
import menu
import gui
import settings
import state
import geometry as geo
import colors
import action


def main_menu(state_stack):
    ui_elements = []
    ui_state = state.UIState(gui.UIElementList(ui_elements))

    start_test_game_function =\
        lambda: ui_state.current_stack.push(gamestate.TestGameState())
    start_game_function =\
        lambda: ui_state.current_stack.push(gamestate.GameState())
    quit_game_function = lambda: ui_state.current_stack.pop()
    dungeon_visualizer_function =\
        lambda: ui_state.current_stack.push(dungeoncreatorvisualizer.
                                            DungeonCreatorVisualizer())

    start_test_game_option =\
        menu.MenuOptionWithSymbols("Start Test Dungeon",
                                   "(", " ",
                                   start_test_game_function)
    start_game_option = menu.MenuOptionWithSymbols("Start Dungeon",
                                                   "(", " ",
                                                   start_game_function)
    dungeon_creator_option =\
        menu.MenuOptionWithSymbols("Dungeon Creator",
                                   "(", " ",
                                   dungeon_visualizer_function)
    quit_option =\
        menu.MenuOptionWithSymbols("Quit", "(", " ", quit_game_function)

    menu_items = [start_test_game_option, start_game_option,
                  dungeon_creator_option, quit_option]

    border = 4
    temp_position = (-1, -1)
    main_menu = menu.StaticMenu(temp_position,
                                menu_items, state_stack,
                                margin=settings.menu_theme.margin,
                                vertical_space=1)
    main_menu_rect =\
        rectfactory.ratio_of_screen_rect(main_menu.width + border,
                                         main_menu.height + border, 0.5, 0.8)
    main_menu.offset = main_menu_rect.top_left

    background_rect = gui.StyledRectangle(main_menu_rect,
                                          settings.menu_theme.rect_style)
    ui_elements.append(background_rect)
    ui_elements.append(main_menu)
    return ui_state


def inventory_menu(player, state_stack):
    right_side_menu_rect = rectfactory.right_side_menu_rect()
    menu_stack_panel = gui.StackPanelVertical(right_side_menu_rect.top_left)
    heading = gui.TextBox("Inventory:", geo.zero2d(),
                          colors.INVENTORY_HEADING,
                          margin=settings.menu_theme.margin)
    menu_stack_panel.append(heading)

    inventory_menu_rect = geo.Rect(geo.zero2d(),
                                   right_side_menu_rect.width,
                                   right_side_menu_rect.height)
    inventory_menu = menu.InventoryMenu(inventory_menu_rect.top_left,
                                        player, state_stack,
                                        margin=settings.menu_theme.margin)
    menu_stack_panel.append(inventory_menu)

    inventory_menu_bg =\
        gui.StyledRectangle(right_side_menu_rect,
                            settings.menu_theme.rect_style)

    ui_elements = [inventory_menu_bg, menu_stack_panel]
    ui_state = state.UIState(gui.UIElementList(ui_elements))
    return ui_state


def item_actions_menu(item, player, state_stack):
    right_side_menu_rect = rectfactory.right_side_menu_rect()
    menu_stack_panel = gui.StackPanelVertical(right_side_menu_rect.top_left)
    heading = gui.TextBox(item.name, geo.zero2d(),
                          colors.INVENTORY_HEADING,
                          margin=settings.menu_theme.margin)
    menu_stack_panel.append(heading)

    item_actions_menu_rect = geo.Rect(geo.zero2d(),
                                      right_side_menu_rect.width,
                                      right_side_menu_rect.height)
    item_actions_menu =\
        menu.ItemActionsMenu(item_actions_menu_rect.top_left,
                             item, player, state_stack,
                             margin=settings.menu_theme.margin)
    menu_stack_panel.append(item_actions_menu)

    inventory_menu_bg =\
        gui.StyledRectangle(right_side_menu_rect,
                            settings.menu_theme.rect_style)

    ui_elements = [inventory_menu_bg, menu_stack_panel]
    ui_state = state.UIState(gui.UIElementList(ui_elements))
    return ui_state


def equipment_menu(player, state_stack):
    right_side_menu_rect = rectfactory.right_side_menu_rect()
    menu_stack_panel = gui.StackPanelVertical(right_side_menu_rect.top_left)
    heading = gui.TextBox("Equipment:", geo.zero2d(),
                          colors.INVENTORY_HEADING,
                          margin=settings.menu_theme.margin)
    menu_stack_panel.append(heading)

    equipment_menu_rect = geo.Rect(geo.zero2d(),
                                   right_side_menu_rect.width,
                                   right_side_menu_rect.height)

    equipment_menu_bg =\
        gui.StyledRectangle(right_side_menu_rect,
                            settings.menu_theme.rect_style)

    equipment_options = []
    for slot in equipment.EquipmentSlots.ALL:
        slot_menu = equipment_slot_menu(player, slot, state_stack)
        option_func = DelayedStatePush(state_stack, slot_menu)
        item_in_slot = player.equipment.get(slot)
        if(item_in_slot is None):
            item_name = "-"
        else:
            item_name = item_in_slot.name
        equipment_options.append(menu.MenuOptionWithSymbols(item_name,
                                                            slot.symbol,
                                                            slot.symbol,
                                                            option_func))

    resulting_menu = menu.StaticMenu(equipment_menu_rect.top_left,
                                     equipment_options, state_stack,
                                     margin=settings.menu_theme.margin)
    menu_stack_panel.append(resulting_menu)

    ui_elements = [equipment_menu_bg, menu_stack_panel]
    ui_state = state.UIState(gui.UIElementList(ui_elements))
    return ui_state


def equipment_slot_menu(player, equipment_slot, state_stack):
    right_side_menu_rect = rectfactory.right_side_menu_rect()
    menu_stack_panel = gui.StackPanelVertical(right_side_menu_rect.top_left)

    heading = gui.TextBox("Change : " + equipment_slot.name, geo.zero2d(),
                          colors.INVENTORY_HEADING,
                          margin=settings.menu_theme.margin)
    menu_stack_panel.append(heading)

    equipment_menu_rect = geo.Rect(geo.zero2d(),
                                   right_side_menu_rect.width,
                                   right_side_menu_rect.height)
    items =\
        player.inventory.items_of_equipment_type(equipment_slot.equipment_type)
    re_equip_options = []
    for item in items:
        function =\
            (lambda:
             action.ReEquipAction(item).act(source_entity=player,
                                            equipment_slot=equipment_slot))
        re_equip_function =\
            menu.DelayedFunctionCall(state_stack, function, states_to_pop=3)
        re_equip_options.append(menu.MenuOption(item.name, re_equip_function))

    function =\
        (lambda: action.UnEquipAction(player.equipment.get(equipment_slot))
            .act(source_entity=player, target_entity=player,
                 equipment_slot=equipment_slot))
    unequip_function =\
        menu.DelayedFunctionCall(state_stack, function, states_to_pop=3)
    re_equip_options.append(menu.MenuOption("- None -", unequip_function))

    resulting_menu = menu.StaticMenu(equipment_menu_rect.top_left,
                                     re_equip_options, state_stack,
                                     margin=settings.menu_theme.margin)
    menu_stack_panel.append(resulting_menu)

    equipment_menu_bg =\
        gui.StyledRectangle(right_side_menu_rect,
                            settings.menu_theme.rect_style)

    ui_elements = [equipment_menu_bg, menu_stack_panel]
    ui_state = state.UIState(gui.UIElementList(ui_elements))
    return ui_state


def context_menu(player, state_stack):
    current_dungeon_feature =\
        player.dungeon_level.get_tile(player.position).get_dungeon_feature()
    context_options = []
    if(not current_dungeon_feature is None):
        context_options.extend(get_dungeon_feature_menu_options
                               (current_dungeon_feature, state_stack, player))

    inventory_menu_opt = inventory_menu(player, state_stack)
    open_inventory_option =\
        menu.MenuOption("Inventory",
                        lambda: state_stack.push(inventory_menu_opt),
                        not player.inventory.is_empty())
    context_options.append(open_inventory_option)

    equipment_menu_opt = equipment_menu(player, state_stack)
    open_inventory_option =\
        menu.MenuOption("Equipment",
                        lambda: state_stack.push(equipment_menu_opt))
    context_options.append(open_inventory_option)

    context_menu_rect = rectfactory.center_of_screen_rect(30, 30)
    resulting_menu = menu.StaticMenu(context_menu_rect.top_left,
                                     context_options, state_stack,
                                     margin=settings.menu_theme.margin)
    background_rect =\
        gui.StyledRectangle(context_menu_rect,
                            settings.menu_theme.rect_style)

    ui_elements = [background_rect, resulting_menu]
    ui_state = state.UIState(gui.UIElementList(ui_elements))
    return ui_state


def get_dungeon_feature_menu_options(dungeon_feature, state_stack, player):
    feature_options = []
    game_state = player.state_stack.get_game_state()
    for feature_action in dungeon_feature.player_actions:
        feat_function = action.DelayedActionCall(action=feature_action,
                                                 source_entity=player,
                                                 target_entity=player,
                                                 game_state=game_state)
        function =\
            menu.DelayedFunctionCall(state_stack, feat_function,
                                     states_to_pop=1)
        feature_options.append(menu.MenuOption(action.name, function,
                                               action.can_act()))
    return feature_options


class DelayedStatePush(object):
    def __init__(self, state_stack, state):
        self.state_stack = state_stack
        self.state = state

    def __call__(self):
        self.state_stack.push(self.state)