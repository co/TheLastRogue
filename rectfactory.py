import geometry as geo
import inventory
import settings
import constants


def full_screen_rect():
    return geo.Rect(geo.zero2d(), settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)


def center_of_screen_rect(width, height):
    return ratio_of_screen_rect(width, height, 0.5, 0.5)


def ratio_of_screen_rect(width, height, x_ratio, y_ratio):
    x = int((settings.SCREEN_WIDTH - width) * x_ratio)
    y = int((settings.SCREEN_HEIGHT - height) * y_ratio)
    return geo.Rect((x, y), width, height)


def right_side_menu_rect():
    x = settings.SCREEN_WIDTH - constants.RIGHT_SIDE_BAR_WIDTH
    y = 0
    return geo.Rect((x, y), constants.RIGHT_SIDE_BAR_WIDTH, settings.SCREEN_HEIGHT)


def message_display_rect():
    message_display_position =\
        (constants.LEFT_SIDE_BAR_WIDTH, settings.SCREEN_HEIGHT - constants.GUI_BOX_HEIGHT)
    return geo.Rect(message_display_position, constants.MESSAGES_BAR_WIDTH, constants.GUI_BOX_HEIGHT)


def player_status_rect():
    return geo.Rect((0, 0), constants.LEFT_SIDE_BAR_WIDTH, constants.GUI_BOX_HEIGHT)


def monster_status_rect():
    return geo.Rect(geo.zero2d(), constants.LEFT_SIDE_BAR_WIDTH, constants.MONSTER_STATUS_BAR_HEIGHT)


def right_side_menu_rect():
    return geo.Rect((0, 0), constants.RIGHT_SIDE_BAR_WIDTH,  inventory.ITEM_CAPACITY + 8)


def description_rectangle():
    return geo.Rect((0, 0), min(40, settings.SCREEN_WIDTH - constants.RIGHT_SIDE_BAR_WIDTH), 10)


def item_stat_rectangle():
    return geo.Rect((0, 0), min(40, settings.SCREEN_WIDTH - constants.RIGHT_SIDE_BAR_WIDTH), 12)


def command_list_rectangle():
    return geo.Rect((0, 0), constants.RIGHT_SIDE_BAR_WIDTH, constants.GUI_BOX_HEIGHT)
