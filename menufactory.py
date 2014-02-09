import action
import constants
import colors
import dungeoncreatorvisualizer
import gamestate
import gametime
import geometry as geo
import graphic
import gui
import menu
import rectfactory
import settings
import state
import style
import icon


def _main_menu(ui_state, state_stack, player_name_func):
    """
    Creates the first menu of the game.
    """
    continue_game_function = lambda: ui_state.current_stack.push(gamestate.load_first_game())
    start_game_function = lambda: ui_state.current_stack.push(gamestate.GameState(player_name_func()))
    save_game_function = lambda: gamestate.save(ui_state.current_stack.get_game_state())
    start_test_game_function = lambda: ui_state.current_stack.push(gamestate.TestGameState(player_name_func()))
    quit_game_function = lambda: ui_state.current_stack.pop()
    dungeon_visualizer_function = \
        lambda: ui_state.current_stack.push(dungeoncreatorvisualizer.DungeonCreatorVisualizer())

    no_icon = graphic.GraphicChar(None, colors.BLACK, " ")
    gun_icon = graphic.GraphicChar(None, colors.WHITE, icon.GUN)
    menu_items = []

    continue_game_option = menu.MenuOptionWithSymbols("Continue", gun_icon, no_icon, [continue_game_function],
                                                      gamestate.is_there_a_saved_game)
    menu_items.append(continue_game_option)

    start_game_option = \
        menu.MenuOptionWithSymbols("New Game", gun_icon, no_icon, [start_game_function, save_game_function])
    menu_items.append(start_game_option)

    if settings.DEV_MODE_FLAG:
        start_test_game_option = \
            menu.MenuOptionWithSymbols("Test Dungeon", gun_icon, no_icon, [start_test_game_function])
        menu_items.append(start_test_game_option)

        dungeon_creator_option = \
            menu.MenuOptionWithSymbols("Dungeon Generator", gun_icon, no_icon, [dungeon_visualizer_function])
        menu_items.append(dungeon_creator_option)

    quit_option = menu.MenuOptionWithSymbols("Quit", gun_icon, no_icon, [quit_game_function])
    menu_items.append(quit_option)

    temp_position = (0, 0)
    return menu.StaticMenu(temp_position, menu_items, state_stack, margin=style.menu_theme.margin,
                           vertical_space=1, vi_keys_accepted=False)


def get_save_quit_menu(player, state_stack):
    options = []
    game_state = player.game_state.value
    exit_menu_function = menu.BackToGameFunction(state_stack)
    save_and_quit_graphic_active = graphic.GraphicChar(None, colors.WHITE, icon.GUNSLINGER_THIN)
    save_and_quit_graphic_inactive = graphic.GraphicChar(None, colors.GRAY, icon.GUNSLINGER_THIN)
    options.append(menu.MenuOptionWithSymbols("Save and Quit", save_and_quit_graphic_active,
                                              save_and_quit_graphic_inactive,
                                              [lambda: gamestate.save(game_state), exit_menu_function,
                                               game_state.current_stack.pop,
                                               (lambda: player.actor.add_energy_spent(gametime.single_turn))]))

    give_up_graphic_active = graphic.GraphicChar(None, colors.WHITE, icon.CORPSE)
    give_up_graphic_inactive = graphic.GraphicChar(None, colors.GRAY, icon.CORPSE)
    options.append(menu.MenuOptionWithSymbols("Give Up", give_up_graphic_active, give_up_graphic_inactive,
                                              [player.health_modifier.kill, exit_menu_function,
                                               (lambda: player.actor.add_energy_spent(gametime.single_turn))]))

    return get_menu_with_options(options, state_stack, 6, 5)


def start_accept_reject_prompt(state_stack, game_state, message):
    prompt = menu.AcceptRejectPrompt(state_stack, message)
    game_state.start_prompt(state.UIState(prompt))
    return prompt.result


def get_menu_with_options(options, state_stack, x_border=4, y_border=5):
    temp_position = (-1, -1)
    main_menu = menu.StaticMenu(temp_position, options, state_stack, margin=style.menu_theme.margin, vertical_space=1)
    main_menu_rect = rectfactory.ratio_of_screen_rect(main_menu.width + x_border, main_menu.height + y_border - 1, 0.5, 0.8)
    main_menu.offset = main_menu_rect.top_left

    background_rect = get_menu_background(main_menu_rect)
    ui_state = state.UIState(gui.UIElementList([background_rect, main_menu]))
    return ui_state


def inventory_menu(player, state_stack):
    menu_stack_panel = gui.StackPanelVertical((2, 2), vertical_space=1)
    heading_stack = gui.StackPanelHorizontal((0, 1), horizontal_space=1)
    heading_stack.append(gui.SymbolUIElement((0, 0), graphic.GraphicChar(None, colors.INVENTORY_HEADING,
                                                                         icon.INVENTORY_ICON)))
    heading_stack.append(gui.TextBox("Inventory", (0, 0), colors.INVENTORY_HEADING))
    menu_stack_panel.append(heading_stack)

    description_card = gui.DescriptionCard(rectfactory.description_rectangle(), style.rogue_classic_theme)
    inventory_menu = menu.InventoryMenu((0, 1), player, state_stack, description_card, (0, 0), vertical_space=0)
    menu_stack_panel.append(inventory_menu)

    inventory_menu_bg = gui.StyledRectangle(rectfactory.right_side_menu_rect(), style.MinimalChestStyle())
    inventory_gui = gui.UIElementList([inventory_menu_bg, menu_stack_panel])

    inventory_stack_panel = gui.StackPanelHorizontal((0, 0), alignment=gui.StackPanelHorizontal.ALIGN_BOTTOM)
    inventory_stack_panel.append(description_card)
    inventory_stack_panel.append(inventory_gui)

    dock = gui.UIDock(rectfactory.full_screen_rect())
    dock.bottom_right = inventory_stack_panel
    return state.UIState(dock)


def has_item_with_action_tag(player, item_action_tag):
    for item in player.inventory.get_items_sorted():
        if len(item.get_children_with_tag(item_action_tag)) > 0:
            return True
    return False


def filtered_by_action_item_menu(player, state_stack, item_action_tag, heading_text):
    menu_stack_panel = gui.StackPanelVertical((0, 0), vertical_space=0)
    heading = gui.TextBox(heading_text, (2, 1), colors.INVENTORY_HEADING, margin=style.menu_theme.margin)
    menu_stack_panel.append(heading)

    stack_pop_function = menu.BackToGameFunction(state_stack)
    description_card = gui.DescriptionCard(rectfactory.description_rectangle(), style.rogue_classic_theme)

    menu_items = []
    for item in player.inventory.get_items_sorted():
        if len(item.get_children_with_tag(item_action_tag)) > 0:
            item_action = item.get_children_with_tag(item_action_tag)[0]
            menu_items.append(menu.MenuOptionWithSymbols(
                menu.get_item_option_text(item), item.graphic_char, item.graphic_char,
                [action.DelayedFunctionCall(item_action.act, source_entity=player,
                                            target_entity=player), stack_pop_function],
                can_activate=(lambda: item_action.can_act(source_entity=player,
                                                          target_entity=player)),
                description=item.description))

    _equip_menu = menu.StaticMenu(rectfactory.right_side_menu_rect().top_left, menu_items, state_stack,
                                  margin=style.menu_theme.margin, vertical_space=0, description_card=description_card)

    menu_stack_panel.append(_equip_menu)

    menu_bg = gui.StyledRectangle(rectfactory.right_side_menu_rect(), style.MinimalChestStyle())
    menu_gui = gui.UIElementList([menu_bg, menu_stack_panel])

    inventory_stack_panel = gui.StackPanelHorizontal((0, 0), alignment=gui.StackPanelHorizontal.ALIGN_BOTTOM)
    inventory_stack_panel.append(description_card)
    inventory_stack_panel.append(menu_gui)

    dock = gui.UIDock(rectfactory.full_screen_rect())
    dock.bottom_right = inventory_stack_panel
    return state.UIState(dock)


def item_actions_menu(item, player, state_stack):
    menu_stack_panel = gui.StackPanelVertical((2, 2), vertical_space=1)
    heading_stack = gui.StackPanelHorizontal((0, 1), horizontal_space=1)
    heading_stack.append(gui.SymbolUIElement((0, 0), item.graphic_char))
    heading = gui.TextBox(item.description.name, (0, 0), colors.INVENTORY_HEADING)
    heading_stack.append(heading)
    menu_stack_panel.append(heading_stack)

    item_actions_menu = menu.ItemActionsMenu((0, 0), item, player, state_stack, margin=(2, 2))
    menu_stack_panel.append(item_actions_menu)
    inventory_menu_bg = gui.StyledRectangle(rectfactory.right_side_menu_rect(),
                                            style.rogue_classic_theme.rect_style)

    dock = gui.UIDock(rectfactory.full_screen_rect())
    ui_elements = [inventory_menu_bg, menu_stack_panel]
    dock.bottom_right = gui.UIElementList(ui_elements)
    ui_state = state.UIState(dock)
    return ui_state


def equipment_menu(player, state_stack):
    menu_stack_panel = gui.StackPanelVertical((0, 0), margin=(0, 0))
    heading = gui.TextBox("Equipment", (2, 1), colors.INVENTORY_HEADING, (2, 2))
    menu_stack_panel.append(heading)

    equipment_menu_bg = gui.StyledRectangle(rectfactory.right_side_menu_rect(),
                                            style.rogue_classic_theme.rect_style)

    description_card = gui.DescriptionCard(rectfactory.description_rectangle(), style.rogue_classic_theme)
    resulting_menu = menu.EquipmentMenu((0, 0), player, state_stack, description_card=description_card,
                                        margin=(2, 1))
    menu_stack_panel.append(resulting_menu)

    equipment_gui = gui.UIElementList([equipment_menu_bg, menu_stack_panel])

    equipment_stack_panel = gui.StackPanelHorizontal((0, 0), alignment=gui.StackPanelHorizontal.ALIGN_BOTTOM)
    equipment_stack_panel.append(description_card)
    equipment_stack_panel.append(equipment_gui)

    dock = gui.UIDock(rectfactory.full_screen_rect())
    dock.bottom_right = equipment_stack_panel
    return state.UIState(dock)


def equipment_slot_menu(player, equipment_slot, state_stack):
    """
Creates a menu which shows the possible actions
that can be taken on a given equipment_slot.
"""
    menu_stack_panel = gui.StackPanelVertical((0, 0), margin=(0, 0))
    heading = gui.TextBox("Change " + equipment_slot.name, (2, 1), colors.INVENTORY_HEADING, (2, 2))
    menu_stack_panel.append(heading)

    description_card = gui.DescriptionCard(rectfactory.description_rectangle(), style.rogue_classic_theme)
    resulting_menu = menu.EquipSlotMenu((0, 0), player, equipment_slot, state_stack, description_card, (2, 1))
    menu_stack_panel.append(resulting_menu)

    equipment_menu_bg = gui.StyledRectangle(rectfactory.right_side_menu_rect(),
                                            style.rogue_classic_theme.rect_style)
    equipment_slot_gui = gui.UIElementList([equipment_menu_bg, menu_stack_panel])

    equipment_slot_stack_panel = gui.StackPanelHorizontal((0, 0), alignment=gui.StackPanelHorizontal.ALIGN_BOTTOM)
    equipment_slot_stack_panel.append(description_card)
    equipment_slot_stack_panel.append(equipment_slot_gui)

    dock = gui.UIDock(rectfactory.full_screen_rect())
    dock.bottom_right = equipment_slot_stack_panel
    return state.UIState(dock)


def get_menu_background(rectangle):
    background_rect = gui.StyledRectangle(rectangle, style.menu_theme.rect_style)
    return background_rect


def context_menu(player, state_stack):
    current_dungeon_feature = (player.dungeon_level.value.get_tile(player.position.value).get_dungeon_feature())
    context_options = []
    stack_pop_function = menu.BackToGameFunction(state_stack)
    if not current_dungeon_feature is None:
        context_options.extend(get_dungeon_feature_menu_options(player, stack_pop_function))

    inventory_menu_opt = inventory_menu(player, state_stack)
    open_inventory_option = menu.MenuOption("Inventory", [lambda: state_stack.push(inventory_menu_opt)],
                                            (lambda: not player.inventory.is_empty()))
    context_options.append(open_inventory_option)

    equipment_menu_opt = equipment_menu(player, state_stack)
    open_equipment_option = menu.MenuOption("Equipment", [lambda: state_stack.push(equipment_menu_opt)])
    context_options.append(open_equipment_option)

    context_menu_rect = rectfactory.center_of_screen_rect(max(option.width for option in context_options) + 4,
                                                          len(context_options) * 2 + 3)
    resulting_menu = menu.StaticMenu(context_menu_rect.top_left, context_options, state_stack,
                                     margin=style.menu_theme.margin)
    background_rect = get_menu_background(context_menu_rect)

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
        feature_options.append(menu.MenuOption(feature_action.name, functions, feature_action.can_act))
    return feature_options


def title_screen(state_stack):
    title_stack_panel = gui.StackPanelVertical((0, 0), alignment=gui.StackPanelVertical.ALIGN_CENTER)
    line = gui.HorizontalLine(icon.H_LINE, colors.GRAY,
                              colors.WHITE, settings.SCREEN_WIDTH + 1)
    the_text = gui.TextBox("T H E", (0, 0), colors.BLACK, (0, 1))
    last_text = gui.TextBox("L A S T", (0, 0), colors.BLACK, (0, 1))
    rogue_text = gui.TextBox("R O G U E", (0, 0), colors.BLACK, (0, 1))

    vspace = gui.VerticalSpace(15)

    hero_name_type_writer = gui.TypeWriter((0, 0), colors.WHITE, colors.GRAY_D, constants.LEFT_SIDE_BAR_WIDTH - 4,
                                           default_text=settings.DEFAULT_PLAYER_NAME)

    title_stack_panel.append(vspace)
    title_stack_panel.append(line)
    title_stack_panel.append(the_text)
    title_stack_panel.append(last_text)
    title_stack_panel.append(rogue_text)
    title_stack_panel.append(line)
    title_stack_panel.append(gui.VerticalSpace(5))

    bg_rect = gui.FilledRectangle(rectfactory.full_screen_rect(), colors.DARK_BLUE)
    bg_sign_rect = gui.FilledRectangle(geo.Rect((0, 15), settings.SCREEN_WIDTH, 11), colors.WHITE)

    ui_state = state.UIState(gui.UIElementList(None))
    main_menu = _main_menu(ui_state, state_stack, lambda: hero_name_type_writer.text)
    border_x = 6
    border_y = 4
    menu_bg = get_menu_background(geo.Rect((0, 0), main_menu.width + border_x, main_menu.height + border_y))
    menu_and_bg = gui.UIElementList([menu_bg, main_menu])

    name_heading = gui.TextBox("Name:", (0, 0), colors.CYAN_D, (0, 1))
    menu_stack_panel = gui.StackPanelVertical((0, 0), (0, 0), vertical_space=0,
                                              alignment=gui.StackPanelVertical.ALIGN_CENTER)
    menu_stack_panel.append(name_heading)
    menu_stack_panel.append(hero_name_type_writer)
    menu_stack_panel.append(gui.VerticalSpace(1))
    menu_stack_panel.append(menu_and_bg)
    menu_stack_panel.append(gui.VerticalSpace(2))

    dock = gui.UIDock(rectfactory.full_screen_rect())
    dock.bottom = menu_stack_panel

    type_writer_highlight_update = \
        gui.UpdateCallOnlyElement(
            [lambda: type_writer_highlight_update_function(name_heading, hero_name_type_writer,
                                                           main_menu, colors.WHITE,
                                                           colors.GRAY_D, [1, 2])])

    ui_state.ui_element.elements = [bg_rect, bg_sign_rect, title_stack_panel, dock, type_writer_highlight_update]
    return ui_state


def type_writer_highlight_update_function(label, type_writer, menu, active_fg_color, inactive_fg_color,
                                          active_indices):
    """
Function for manipulating typewriter color, depending on selected menu item.

This is a ugly hack, remove if some event system is implemented for menus.
"""
    if menu.selected_index in active_indices:
        label.color_fg = active_fg_color
        type_writer.is_active = True
    else:
        label.color_fg = inactive_fg_color
        type_writer.is_active = False


def victory_screen(state_stack):
    victory_stack_panel = gui.StackPanelVertical((0, 0), alignment=gui.StackPanelVertical.ALIGN_CENTER)
    line = gui.HorizontalLine(icon.H_LINE, colors.YELLOW,
                              None, settings.SCREEN_WIDTH + 1)
    victory_text = gui.TextBox("A WINNER IS YOU", (0, 0), colors.WHITE)
    ironic_text = \
        gui.TextBox("Good job! No seriously, I bet it was real hard...",
                    (0, 0), colors.YELLOW_D)

    continue_option = \
        menu.MenuOption("Press Enter to Continue...", [lambda: state_stack.pop_to_main_menu()])

    continue_menu = menu.StaticMenu((0, 0), [continue_option], state_stack,
                                    margin=style.menu_theme.margin, may_escape=False)

    short_vspace = gui.VerticalSpace(7)
    long_vspace = gui.VerticalSpace(settings.SCREEN_HEIGHT - 22)

    victory_stack_panel.append(short_vspace)
    victory_stack_panel.append(line)
    victory_stack_panel.append(victory_text)
    victory_stack_panel.append(line)
    victory_stack_panel.append(ironic_text)
    victory_stack_panel.append(long_vspace)
    victory_stack_panel.append(continue_menu)

    grayout_rect = gui.RectangleChangeColor(rectfactory.full_screen_rect(), colors.DARK_BROWN, colors.YELLOW_D)

    ui_elements = [grayout_rect, victory_stack_panel]
    ui_state = state.UIState(gui.UIElementList(ui_elements))
    return ui_state


def game_over_screen(state_stack):
    game_over_stack_panel = gui.StackPanelVertical((0, 0), alignment=gui.StackPanelVertical.ALIGN_CENTER)
    red_line = gui.HorizontalLine(icon.H_LINE, colors.RED,
                                  colors.BLACK, settings.SCREEN_WIDTH + 1)
    game_over_text = gui.TextBox("YOU DIED", (0, 0), colors.RED)
    insult_text = gui.TextBox("Like a bitch.", (0, 0), colors.DARK_BROWN)

    continue_option = \
        menu.MenuOption("Press Enter to Accept Your Fate...",
                        [lambda: state_stack.pop_to_main_menu()])

    continue_menu = menu.StaticMenu((0, 0), [continue_option], state_stack,
                                    margin=style.menu_theme.margin, may_escape=False)

    short_vspace = gui.VerticalSpace(7)
    long_vspace = gui.VerticalSpace(settings.SCREEN_HEIGHT - 22)

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
