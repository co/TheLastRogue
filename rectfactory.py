import geometry as geo
import settings


def full_screen_rect():
    return geo.Rect(geo.zero2d(),
                    settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)


def center_of_screen_rect(width, height):
    return ratio_of_screen_rect(width, height, 0.5, 0.5)


def ratio_of_screen_rect(width, height, x_ratio, y_ratio):
    x = (settings.WINDOW_WIDTH - width) * x_ratio
    y = (settings.WINDOW_HEIGHT - height) * y_ratio
    return geo.Rect(geo.Vector2D(x, y), width, height)
