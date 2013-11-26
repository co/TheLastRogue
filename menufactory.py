from equipactions import UnequipAction
import colors
import dungeoncreatorvisualizer
import equipment
import gamestate
import geometry as geo
import gui
import menu
import rectfactory
import settings
import state
import style
import icon


def _main_menu_ui_elements(ui_state, state_stack):
    """
    Creates the first menu of the game.
    """
    continue_game_function = \
        lambda: ui_state.current_stack.push(gamestate.load_first_game())
    start_game_function = \
        lambda: ui_state.current_stack.push(gamestate.GameState())
    start_test_game_function = \
        lambda: ui_state.current_stack.push(gamestate.TestGameState())
    quit_game_function = lambda: ui_state.current_stack.pop()
    dungeon_visualizer_function = \
        lambda: ui_state.current_stack.push(dungeoncreatorvisualizer.DungeonCreatorVisualizer())

    continue_game_option = \
        menu.MenuOptionWithSymbols("Continue",
                                   icon.GUN, " ",
                                   [continue_game_function],
                                   gamestate.is_there_a_saved_game())

    start_game_option = \
        menu.MenuOptionWithSymbols("Start Dungeon",
                                   icon.GUN, " ",
                                   [start_game_function])
    start_test_game_option = \
        menu.MenuOptionWithSymbols("Start Test Dungeon",
                                   icon.GUN, " ",
                                   [start_test_game_function])
    dungeon_creator_option = \
        menu.MenuOptionWithSymbols("Dungeon Creator",
                                   icon.GUN, " ",
                                   [dungeon_visualizer_function])
    quit_option = menu.MenuOptionWithSymbols("Quit", icon.GUN,
                                             " ", [quit_game_function])

    menu_items = [continue_game_option, start_game_option, start_test_game_option,
                  dungeon_creator_option, quit_option]

    border = 4
    temp_position = (-1, -1)
    main_menu = menu.StaticMenu(temp_position,
                                menu_items, state_stack,
                                margin=style.menu_theme.margin,
                                vertical_space=1)
    main_menu_rect = \
        rectfactory.ratio_of_screen_rect(main_menu.width + border,
                                         main_menu.height + border - 1, 0.5, 0.8)
    main_menu.offset = main_menu_rect.top_left

    background_rect = \
        gui.StyledRectangle(main_menu_rect, style.menu_theme.rect_style)
    ui_elements = [background_rect, main_menu]
    return ui_elements


def get_menu_with_options(options, state_stack):
    border = 4
    temp_position = (-1, -1)
    main_menu = menu.StaticMenu(temp_position,
                                options, state_stack,
                                margin=style.menu_theme.margin,
                                vertical_space=1)
    main_menu_rect = \
        rectfactory.ratio_of_screen_rect(main_menu.width + border,
                                         main_menu.height + border - 1, 0.5, 0.8)
    main_menu.offset = main_menu_rect.top_left

    background_rect = \
        gui.StyledRectangle(main_menu_rect, style.menu_theme.rect_style)
    ui_state = state.UIState(gui.UIElementList([background_rect, main_menu]))
    return ui_state


def inventory_menu(player, state_stack):
    right_side_menu_rect = rectfactory.right_side_menu_rect()
    menu_stack_panel = gui.StackPanelVertical(right_side_menu_rect.top_left)
    heading = gui.TextBox("Inventory:", geo.zero2d(),
                          colors.INVENTORY_HEADING,
                          margin=style.menu_theme.margin)
    menu_stack_panel.append(heading)

    inventory_menu_rect = geo.Rect(geo.zero2d(),
                                   right_side_menu_rect.width,
                                   right_side_menu_rect.height)
    inventory_menu = \
        menu.InventoryMenu(inventory_menu_rect.top_left, player, state_stack,
                           margin=style.menu_theme.margin)
    menu_stack_panel.append(inventory_menu)

    inventory_menu_bg = \
        gui.StyledRectangle(right_side_menu_rect,
                            style.menu_theme.rect_style)

    ui_elements = [inventory_menu_bg, menu_stack_panel]
    ui_state = state.UIState(gui.UIElementList(ui_elements))
    return ui_state


def item_actions_menu(item, player, state_stack):
    right_side_menu_rect = rectfactory.right_side_menu_rect()
    menu_stack_panel = gui.StackPanelVertical(right_side_menu_rect.top_left)
    heading = gui.TextBox(item.description.name, geo.zero2d(),
                          colors.INVENTORY_HEADING,
                          margin=style.menu_theme.margin)
    menu_stack_panel.append(heading)

    item_actions_menu_rect = geo.Rect(geo.zero2d(),
                                      right_side_menu_rect.width,
                                      right_side_menu_rect.height)
    item_actions_menu = \
        menu.ItemActionsMenu(item_actions_menu_rect.top_left,
                             item, player, state_stack,
                             margin=style.menu_theme.margin)
    menu_stack_panel.append(item_actions_menu)

    inventory_menu_bg = \
        gui.StyledRectangle(right_side_menu_rect,
                            style.menu_theme.rect_style)

    ui_elements = [inventory_menu_bg, menu_stack_panel]
    ui_state = state.UIState(gui.UIElementList(ui_elements))
    return ui_state


def equipment_menu(player, state_stack):
    right_side_menu_rect = rectfactory.right_side_menu_rect()
    menu_stack_panel = gui.StackPanelVertical(right_side_menu_rect.top_left)
    heading = gui.TextBox("Equipment:", geo.zero2d(),
                          colors.INVENTORY_HEADING,
                          margin=style.menu_theme.margin)
    menu_stack_panel.append(heading)

    equipment_menu_rect = geo.Rect(geo.zero2d(),
                                   right_side_menu_rect.width,
                                   right_side_menu_rect.height)

    equipment_menu_bg = \
        gui.StyledRectangle(right_side_menu_rect,
                            style.menu_theme.rect_style)

    equipment_options = []
    #slots_with_items = [slot for slot in equipment.EquipmentSlots.ALL
    #if not player.equipment.get(slot) is None]
    for slot in equipment.EquipmentSlots.ALL:
        slot_menu = equipment_slot_menu(player, slot, state_stack)
        option_func = DelayedStatePush(state_stack, slot_menu)
        item_in_slot = player.equipment.get(slot)
        if (item_in_slot is None):
            item_name = "-"
        else:
            item_name = item_in_slot.description.name
        equipment_options.append(menu.MenuOptionWithSymbols(item_name,
                                                            slot.icon,
                                                            slot.icon,
                                                            [option_func]))

    resulting_menu = menu.StaticMenu(equipment_menu_rect.top_left,
                                     equipment_options, state_stack,
                                     margin=style.menu_theme.margin)
    menu_stack_panel.append(resulting_menu)

    ui_elements = [equipment_menu_bg, menu_stack_panel]
    ui_state = state.UIState(gui.UIElementList(ui_elements))
    return ui_state


def equipment_slot_menu(player, equipment_slot, state_stack):
    """
    Creates a menu which shows the possible actions
    that can be taken on a given equipment_slot.
    """
    right_side_menu_rect = rectfactory.right_side_menu_rect()
    menu_stack_panel = gui.StackPanelVertical(right_side_menu_rect.top_left)

    heading = gui.TextBox("Change : " + equipment_slot.name, geo.zero2d(),
                          colors.INVENTORY_HEADING,
                          margin=style.menu_theme.margin)
    menu_stack_panel.append(heading)

    equipment_menu_rect = geo.Rect(geo.zero2d(),
                                   right_side_menu_rect.width,
                                   right_side_menu_rect.height)
    items = \
        player.inventory.items_of_equipment_type(equipment_slot.equipment_type)
    re_equip_options = []
    for item in items:
        reequip_function = \
            item.reequip_action.delayed_call(source_entity=player,
                                             target_entity=player,
                                             equipment_slot=equipment_slot)
        stack_pop_function = menu.StackPopFunction(state_stack, 3)
        functions = [reequip_function, stack_pop_function]
        re_equip_options.append(menu.MenuOption(item.description.name,
                                                functions))

    unequip_function = \
        UnequipAction().delayed_call(source_entity=player,
                                     target_entity=player,
                                     equipment_slot=equipment_slot)
    stack_pop_function = menu.StackPopFunction(state_stack, 3)
    functions = [unequip_function, stack_pop_function]

    re_equip_options.append(menu.MenuOption("- None -", functions))

    resulting_menu = menu.StaticMenu(equipment_menu_rect.top_left,
                                     re_equip_options, state_stack,
                                     margin=style.menu_theme.margin)
    menu_stack_panel.append(resulting_menu)

    equipment_menu_bg = gui.StyledRectangle(right_side_menu_rect,
                                            style.menu_theme.rect_style)

    ui_elements = [equipment_menu_bg, menu_stack_panel]
    ui_state = state.UIState(gui.UIElementList(ui_elements))
    return ui_state


def context_menu(player, state_stack):
    current_dungeon_feature = \
        (player.dungeon_level.value.
         get_tile(player.position.value).get_dungeon_feature())
    context_options = []
    stack_pop_function = menu.BackToGameFunction(state_stack)
    if not current_dungeon_feature is None:
        context_options.extend(get_dungeon_feature_menu_options(player, stack_pop_function))

    inventory_menu_opt = inventory_menu(player, state_stack)
    open_inventory_option = \
        menu.MenuOption("Inventory",
                        [lambda: state_stack.push(inventory_menu_opt)],
                        not player.inventory.is_empty())
    context_options.append(open_inventory_option)

    equipment_menu_opt = equipment_menu(player, state_stack)
    open_equipment_option = \
        menu.MenuOption("Equipment",
                        [lambda: state_stack.push(equipment_menu_opt)])
    context_options.append(open_equipment_option)

    context_menu_rect = rectfactory.center_of_screen_rect(16, 8)
    resulting_menu = menu.StaticMenu(context_menu_rect.top_left,
                                     context_options, state_stack,
                                     margin=style.menu_theme.margin)
    background_rect = \
        gui.StyledRectangle(context_menu_rect,
                            style.menu_theme.rect_style)

    ui_elements = [background_rect, resulting_menu]
    ui_state = state.UIState(gui.UIElementList(ui_elements))
    return ui_state


def get_tile_actions(player):
    tile = player.dungeon_level.value.get_tile(player.position.value)
    dungeon_feature = tile.get_dungeon_feature()
    actions = []
    if not dungeon_feature is None:
        actions = dungeon_feature.get_children_with_tag("user_action")
    return actions


def get_dungeon_feature_menu_options(player, stack_pop_function):
    feature_options = []
    game_state = player.game_state.value
    for feature_action in get_tile_actions(player):
        feature_option = feature_action.delayed_call(source_entity=player,
                                                     target_entity=player,
                                                     game_state=game_state)
        functions = [feature_option, stack_pop_function]
        feature_options.append(menu.MenuOption(feature_action.name, functions,
                                               feature_action.can_act()))
    return feature_options


def title_screen(state_stack):
    title_stack_panel = gui.StackPanelVerticalCentering((0, 0))
    line = gui.HorizontalLine(icon.H_LINE, colors.GRAY,
                              colors.WHITE, settings.WINDOW_WIDTH)
    the_text = gui.TextBox("T H E", (0, 0), colors.BLACK, (0, 1))
    last_text = gui.TextBox("L A S T", (0, 0), colors.BLACK, (0, 1))
    rogue_text = gui.TextBox("R O G U E", (0, 0), colors.BLACK, (0, 1))

    vspace = gui.VerticalSpace(15)

    title_stack_panel.append(vspace)
    title_stack_panel.append(line)
    title_stack_panel.append(the_text)
    title_stack_panel.append(last_text)
    title_stack_panel.append(rogue_text)
    title_stack_panel.append(line)

    bg_rect = gui.FilledRectangle(rectfactory.full_screen_rect(),
                                  colors.DARK_BLUE)

    bg_sign_rect = gui.FilledRectangle(geo.Rect((0, 15),
                                                settings.WINDOW_WIDTH, 11),
                                       colors.WHITE)

    ui_state = state.UIState(gui.UIElementList(None))
    ui_elements = _main_menu_ui_elements(ui_state, state_stack)

    ui_state.ui_element.elements = [bg_rect, bg_sign_rect,
                                    title_stack_panel] + ui_elements
    return ui_state


def victory_screen(state_stack):
    victory_stack_panel = gui.StackPanelVerticalCentering((0, 0))
    line = gui.HorizontalLine(icon.H_LINE, colors.YELLOW,
                              None, settings.WINDOW_WIDTH)
    victory_text = gui.TextBox("A WINNER IS YOU", (0, 0), colors.WHITE)
    ironic_text = \
        gui.TextBox("Good job! No seriously, I bet it was real hard...",
                    (0, 0), colors.YELLOW_D)

    continue_option = \
        menu.MenuOption("Press Enter to Continue...",
                        [lambda: state_stack.pop_to_main_menu()], True)

    continue_menu = menu.StaticMenu((0, 0), [continue_option], state_stack,
                                    margin=style.menu_theme.margin, may_escape=False)

    short_vspace = gui.VerticalSpace(7)
    long_vspace = gui.VerticalSpace(settings.WINDOW_HEIGHT - 18)

    victory_stack_panel.append(short_vspace)
    victory_stack_panel.append(line)
    victory_stack_panel.append(victory_text)
    victory_stack_panel.append(line)
    victory_stack_panel.append(ironic_text)
    victory_stack_panel.append(long_vspace)
    victory_stack_panel.append(continue_menu)

    grayout_rect = gui.RectangleChangeColor(rectfactory.full_screen_rect(),
                                            colors.DARK_BROWN, colors.YELLOW_D)

    ui_elements = [grayout_rect, victory_stack_panel]
    ui_state = state.UIState(gui.UIElementList(ui_elements))
    return ui_state


def game_over_screen(state_stack):
    game_over_stack_panel = gui.StackPanelVerticalCentering((0, 0))
    red_line = gui.HorizontalLine(icon.H_LINE, colors.RED,
                                  colors.BLACK, settings.WINDOW_WIDTH)
    game_over_text = gui.TextBox("YOU DIED", (0, 0), colors.RED)
    insult_text = gui.TextBox("Like a bitch.", (0, 0), colors.DARK_BROWN)

    continue_option = \
        menu.MenuOption("Press Enter to Accept Your Fate...",
                        [lambda: state_stack.pop_to_main_menu()], True)

    continue_menu = menu.StaticMenu((0, 0), [continue_option], state_stack,
                                    margin=style.menu_theme.margin, may_escape=False)

    short_vspace = gui.VerticalSpace(7)
    long_vspace = gui.VerticalSpace(settings.WINDOW_HEIGHT - 18)

    game_over_stack_panel.append(short_vspace)
    game_over_stack_panel.append(red_line)
    game_over_stack_panel.append(game_over_text)
    game_over_stack_panel.append(red_line)
    game_over_stack_panel.append(insult_text)
    game_over_stack_panel.append(long_vspace)
    game_over_stack_panel.append(continue_menu)

    grayout_rect = gui.RectangleChangeColor(rectfactory.full_screen_rect(),
                                            colors.BLACK, colors.DARK_PURPLE)

    ui_elements = [grayout_rect, game_over_stack_panel]
    ui_state = state.UIState(gui.UIElementList(ui_elements))
    return ui_state


class DelayedStatePush(object):
    def __init__(self, state_stack, state):
        self.state_stack = state_stack
        self.state = state

    def __call__(self):
        self.state_stack.push(self.state)
