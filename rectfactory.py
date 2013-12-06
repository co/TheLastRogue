import geometry as geo
import inventory
import settings
import constants


def full_screen_rect():
    return geo.Rect(geo.zero2d(),
                    settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)


def center_of_screen_rect(width, height):
    return ratio_of_screen_rect(width, height, 0.5, 0.5)


def ratio_of_screen_rect(width, height, x_ratio, y_ratio):
    x = int((settings.WINDOW_WIDTH - width) * x_ratio)
    y = int((settings.WINDOW_HEIGHT - height) * y_ratio)
    return geo.Rect((x, y), width, height)


def right_side_menu_rect():
    x = settings.WINDOW_WIDTH - constants.RIGHT_SIDE_BAR_WIDTH
    y = 0
    return geo.Rect((x, y), constants.RIGHT_SIDE_BAR_WIDTH, settings.WINDOW_HEIGHT)


def message_display_rect():
    message_display_position =\
        (constants.LEFT_SIDE_BAR_WIDTH, settings.WINDOW_HEIGHT - constants.MESSAGES_BAR_HEIGHT)
    return geo.Rect(message_display_position, constants.MESSAGES_BAR_WIDTH, constants.MESSAGES_BAR_HEIGHT)


def player_status_rect():
    return geo.Rect((0, 0), constants.LEFT_SIDE_BAR_WIDTH, constants.MESSAGES_BAR_HEIGHT)

    x = settings.WINDOW_WIDTH - constants.RIGHT_SIDE_BAR_WIDTH
    y = 0
    return geo.Rect((x, y), constants.RIGHT_SIDE_BAR_WIDTH, settings.WINDOW_HEIGHT)


def monster_status_rect():
    return geo.Rect(geo.zero2d(), constants.LEFT_SIDE_BAR_WIDTH, constants.MONSTER_STATUS_BAR_HEIGHT)


def right_side_menu_rect():
    return geo.Rect((0, 0), constants.RIGHT_SIDE_BAR_WIDTH,  inventory.ITEM_CAPACITY + 8)
