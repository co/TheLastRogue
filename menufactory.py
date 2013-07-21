import gamestate
import rectfactory
import dungeoncreatorvisualizer
import menu
import gui
import settings
import state
import geometry as geo
import colors


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

    start_test_game_option = menu.MenuOption("Start Test Dungeon",
                                             start_test_game_function)
    start_game_option = menu.MenuOption("Start Dungeon",
                                        start_game_function)
    dungeon_creator_option = menu.MenuOption("Dungeon Creator",
                                             dungeon_visualizer_function)
    quit_option = menu.MenuOption("Quit", quit_game_function)

    menu_items = [start_test_game_option, start_game_option,
                  dungeon_creator_option, quit_option]

    border = 4
    height = 2 * len(menu_items) + border
    width = max([len(option.text) for option in menu_items]) + border
    main_menu_rect = rectfactory.ratio_of_screen_rect(width, height, 0.5, 0.8)
    main_menu = menu.StaticMenu(main_menu_rect, menu_items, state_stack,
                                margin=settings.menu_theme.margin,
                                vertical_space=1)

    background_rect = gui.StyledRectangle(main_menu_rect,
                                          settings.menu_theme.rect_style)
    ui_elements.append(background_rect)
    ui_elements.append(main_menu)
    return ui_state


def inventory_menu(player, state_stack):
    right_side_menu_rect = rectfactory.right_side_menu_rect()
    menu_stack_panel = gui.StackPanelVertical(right_side_menu_rect.top_left,
                                              right_side_menu_rect.width)
    heading = gui.TextBox("Inventory:", geo.zero2d(),
                          colors.INVENTORY_HEADING,
                          margin=settings.menu_theme.margin)
    menu_stack_panel.append(heading)

    inventory_menu_rect = geo.Rect(geo.zero2d(),
                                   right_side_menu_rect.width,
                                   right_side_menu_rect.height)
    inventory_menu = menu.InventoryMenu(inventory_menu_rect,
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
    menu_stack_panel = gui.StackPanelVertical(right_side_menu_rect.top_left,
                                              right_side_menu_rect.width)
    heading = gui.TextBox(item.name, geo.zero2d(),
                          colors.INVENTORY_HEADING,
                          margin=settings.menu_theme.margin)
    menu_stack_panel.append(heading)

    item_actions_menu_rect = geo.Rect(geo.zero2d(),
                                      right_side_menu_rect.width,
                                      right_side_menu_rect.height)
    item_actions_menu =\
        menu.ItemActionsMenu(item_actions_menu_rect,
                             item, player, state_stack,
                             margin=settings.menu_theme.margin)
    menu_stack_panel.append(item_actions_menu)

    inventory_menu_bg =\
        gui.StyledRectangle(right_side_menu_rect,
                            settings.menu_theme.rect_style)

    ui_elements = [inventory_menu_bg, menu_stack_panel]
    ui_state = state.UIState(gui.UIElementList(ui_elements))
    return ui_state


def context_menu(player, state_stack):
    current_dungeon_feature =\
        player.dungeon_level.get_tile(player.position).get_dungeon_feature()
    context_options = []
    if(not current_dungeon_feature is None):
        context_options.extend(get_dungeon_feature_menu_options
                               (current_dungeon_feature, state_stack, player))

    open_inventory_option =\
        menu.MenuOption("Inventory",
                        lambda: context_menu_open_inventory(player,
                                                            state_stack),
                        not player.inventory.is_empty())
    context_options.append(open_inventory_option)

    context_menu_rect = rectfactory.center_of_screen_rect(30, 30)
    resulting_menu = menu.StaticMenu(context_menu_rect,
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
    for action in dungeon_feature.player_actions:
        function = menu.DelayedAction(state_stack, action, player,
                                      player, states_to_pop=1)
        feature_options.append(menu.MenuOption(action.name, function,
                                               action.can_act()))
    return feature_options


def context_menu_open_inventory(player, state_stack):
    menu = inventory_menu(player, state_stack)
    state_stack.push(menu)
