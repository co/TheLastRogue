import geometry as geo
import settings


def center_of_screen_rect(width, height):
    x = (settings.WINDOW_WIDTH - width) / 2
    y = (settings.WINDOW_HEIGHT - height) / 2
    return geo.Rect(geo.Vector2D(x, y), width, height)
