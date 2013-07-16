import gamestate
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
