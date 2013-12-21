import ConfigParser
import sys

menu_theme = "ff_blue_theme"
interface_theme = "rogue_classic_theme"

DEV_MODE_FLAG = "--dev-mode" in sys.argv

defaults = {
    'resolution_width': '1024',
    'resolution_height': '768',
    'animation_delay': '3',
    'fps': '20',
    'full_screen': 'False',

    'left': 'h',
    'right': 'j',
    'up': 'k',
    'down': 'l',

    'up_left': 'u',
    'up_right': 'i',
    'down_left': 'n',
    'down_right': 'm',

    'inventory': 'b',
    'equipment': 'e',
    'stone': 's',
    'fire': 'f',
    'rest': 'r',
    'examine': 'x',
    'drink': 'q',
    'activate': 'a',
    'wear_wield': 'w'
}

config = ConfigParser.SafeConfigParser(defaults)
config.read('config.txt')

tile_width = 16

if not config.has_section("Screen"):
    config.add_section("Screen")
if not config.has_section("KeyBind"):
    config.add_section("KeyBind")

MINIMUM_RESOLUTION_WIDTH = 1024
MINIMUM_RESOLUTION_HEIGHT = 768

MINIMUM_WIDTH = MINIMUM_RESOLUTION_WIDTH / 16
MINIMUM_HEIGHT = MINIMUM_RESOLUTION_HEIGHT / 16

SCREEN_WIDTH = max(config.getint('Screen', 'resolution_width'), MINIMUM_RESOLUTION_WIDTH) / tile_width
SCREEN_HEIGHT = max(config.getint('Screen', 'resolution_height'), MINIMUM_RESOLUTION_HEIGHT) / tile_width
ANIMATION_DELAY = config.getint('Screen', 'animation_delay')
FULL_SCREEN = config.getboolean('Screen', 'full_screen')
FPS = config.getint('Screen', 'fps')

KEY_LEFT = config.get('KeyBind', 'left')
KEY_RIGHT = config.get('KeyBind', 'right')
KEY_UP = config.get('KeyBind', 'up')
KEY_DOWN = config.get('KeyBind', 'down')

KEY_UP_LEFT = config.get('KeyBind', 'up_left')
KEY_UP_RIGHT = config.get('KeyBind', 'up_right')
KEY_DOWN_LEFT = config.get('KeyBind', 'down_left')
KEY_DOWN_RIGHT = config.get('KeyBind', 'down_right')

KEY_INVENTORY = config.get('KeyBind', 'inventory')
KEY_EQUIPMENT = config.get('KeyBind', 'equipment')
KEY_FIRE = config.get('KeyBind', 'fire')
KEY_REST = config.get('KeyBind', 'rest')
KEY_EXAMINE = config.get('KeyBind', 'examine')
KEY_DRINK = config.get('KeyBind', 'drink')
KEY_ACTIVATE = config.get('KeyBind', 'activate')
KEY_WEAR_WIELD = config.get('KeyBind', 'wear_wield')
