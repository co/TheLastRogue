import ConfigParser
import sys
import getpass

menu_theme = "ff_blue_theme"
interface_theme = "rogue_classic_theme"

DEV_MODE_FLAG = "--dev-mode" in sys.argv

defaults = {
    'resolution_width': '1024',
    'resolution_height': '768',
    'animation_delay': '3',
    'missile_animation_delay': '2',
    'fps': '20',
    'full_screen': 'False',

    'left': 'h',
    'right': 'j',
    'up': 'k',
    'down': 'l',

    'up_left': 'y',
    'up_right': 'u',
    'down_left': 'b',
    'down_right': 'n',

    'inventory': 'i',
    'equipment': 'e',
    'fire': 'f',
    'rest': '.',
    'examine': 'x',
    'auto_explore': 'o',
    'drink': 'q',
    'read': 'r',
    'activate': 'a',
    'wear_wield': 'w',
    'use_pick_up': ',',
    'default_name': getpass.getuser()
}

config = ConfigParser.SafeConfigParser(defaults)
config.read('config.txt')

TILE_WIDTH = 16

# For some reason the parser cries if a section is missing. So if a section is missing we add it.
if not config.has_section("Screen"):
    config.add_section("Screen")
if not config.has_section("KeyBind"):
    config.add_section("KeyBind")
if not config.has_section("Misc"):
    config.add_section("Misc")

MINIMUM_RESOLUTION_WIDTH = 1024
MINIMUM_RESOLUTION_HEIGHT = 768

MINIMUM_WIDTH = MINIMUM_RESOLUTION_WIDTH / 16
MINIMUM_HEIGHT = MINIMUM_RESOLUTION_HEIGHT / 16

SCREEN_WIDTH = max(config.getint('Screen', 'resolution_width'), MINIMUM_RESOLUTION_WIDTH) / TILE_WIDTH
SCREEN_HEIGHT = max(config.getint('Screen', 'resolution_height'), MINIMUM_RESOLUTION_HEIGHT) / TILE_WIDTH

ANIMATION_DELAY = config.getint('Screen', 'animation_delay')
MISSILE_ANIMATION_DELAY = config.getint('Screen', 'missile_animation_delay')
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
KEY_AUTO_EXPLORE = config.get('KeyBind', 'auto_explore')
KEY_DRINK = config.get('KeyBind', 'drink')
KEY_READ = config.get('KeyBind', 'read')
KEY_ACTIVATE = config.get('KeyBind', 'activate')
KEY_WEAR_WIELD = config.get('KeyBind', 'wear_wield')
KEY_USE_PICK_UP = config.get('KeyBind', 'use_pick_up')
DEFAULT_PLAYER_NAME = config.get('Misc', 'default_name')
