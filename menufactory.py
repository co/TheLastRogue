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
    state_stack_panel =\
        gui.StackPanelVertical(geo.zero2d(), settings.WINDOW_WIDTH,
                               colors.INTERFACE_BG, vertical_space=1)
    ui_state = state.UIState(state_stack_panel)

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

    main_menu = menu.StaticMenu(geo.Rect(geo.zero2d(), 30, 10),
                                menu_items, state_stack, vertical_space=1)
    state_stack_panel.append(main_menu)

    return ui_state


def inventory_menu(player, state_stack):
    inventory_menu_rect = geo.Rect(geo.zero2d(),
                                   24,
                                   settings.WINDOW_HEIGHT)
    inventory_position = geo.Vector2D(settings.WINDOW_WIDTH - 24, 0)
    menu_stack_panel = gui.StackPanelVertical(inventory_position,
                                              inventory_menu_rect.width,
                                              colors.INTERFACE_BG)
    heading = gui.TextBox("Inventory:", geo.zero2d(),
                          colors.INVENTORY_HEADING,
                          margin=geo.Vector2D(0, 1))
    menu_stack_panel.append(heading)

    inventory_menu = menu.InventoryMenu(inventory_menu_rect,
                                        player, state_stack)
    menu_stack_panel.append(inventory_menu)

    game_state_grayout_rectangle =\
        gui.RectangleGray(geo.Rect(geo.zero2d(), settings.WINDOW_WIDTH,
                                   settings.WINDOW_HEIGHT), colors.DB_OPAL)

    ui_elements = [game_state_grayout_rectangle, menu_stack_panel]
    ui_state = state.UIState(gui.UIElementSet(ui_elements))
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
                                     context_options, state_stack)
    background_rect = gui.FilledRectangle(context_menu_rect,
                                          colors.INTERFACE_BG)
    ui_elements = [background_rect, resulting_menu]
    ui_state = state.UIState(gui.UIElementSet(ui_elements))
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
