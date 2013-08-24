import palette


################################
# Color definitions
################################

## DawnBringer 16 Palette.
#DB1 = libtcod.Color(20, 12, 28)
#DB2 = libtcod.Color(68, 36, 52)
#DB3 = libtcod.Color(48, 52, 109)
#DB4 = libtcod.Color(78, 74, 78)
#DB5 = libtcod.Color(133, 76, 48)
#DB6 = libtcod.Color(52, 101, 36)
#DB7 = libtcod.Color(208, 70, 72)
#DB8 = libtcod.Color(117, 113, 97)
#DB9 = libtcod.Color(89, 125, 206)
#DB10 = libtcod.Color(210, 125, 44)
#DB11 = libtcod.Color(133, 149, 161)
#DB12 = libtcod.Color(109, 170, 44)
#DB13 = libtcod.Color(210, 170, 153)
#DB14 = libtcod.Color(109, 194, 202)
#DB15 = libtcod.Color(218, 212, 94)
#DB16 = libtcod.Color(222, 238, 214)
#
## DawnBringer 32 Palette.
#DB_BLACK = libtcod.Color(0, 0, 0)
#DB_VALHALLA = libtcod.Color(34, 32, 52)
#DB_LOULOU = libtcod.Color(69, 40, 60)
#DB_OILED_CEDAR = libtcod.Color(102, 57, 49)
#DB_ROPE = libtcod.Color(143, 86, 59)
#DB_TAHITI_GOLD = libtcod.Color(223, 113, 38)
#DB_TWINE = libtcod.Color(217, 160, 102)
#DB_PANCHO = libtcod.Color(238, 195, 154)
#
#DB_GOLDEN_FIZZ = libtcod.Color(251, 242, 54)
#DB_ATLANTIS = libtcod.Color(153, 229, 80)
#DB_CHRISTI = libtcod.Color(106, 190, 48)
#DB_ELF_GREEN = libtcod.Color(55, 148, 110)
#DB_DELL = libtcod.Color(75, 105, 47)
#DB_VERDIGRIS = libtcod.Color(82, 75, 36)
#DB_OPAL = libtcod.Color(50, 60, 57)
#DB_DEEP_KOAMARU = libtcod.Color(63, 63, 116)
#
#DB_VENICE_BLUE = libtcod.Color(48, 96, 130)
#DB_ROYAL_BLUE = libtcod.Color(91, 110, 225)
#DB_CORNFLOWER = libtcod.Color(99, 155, 255)
#DB_VIKING = libtcod.Color(95, 205, 228)
#DB_LIGHT_STEEL_BLUE = libtcod.Color(203, 219, 252)
#DB_WHITE = libtcod.Color(255, 255, 255)
#DB_HEATHER = libtcod.Color(155, 173, 183)
#DB_TOPAZ = libtcod.Color(132, 126, 135)
#
#DB_DIM_GRAY = libtcod.Color(105, 106, 106)
#DB_SMOKEY_ASH = libtcod.Color(89, 86, 82)
#DB_CLAIRVOYANT = libtcod.Color(118, 66, 138)
#DB_BROWN = libtcod.Color(172, 50, 50)
#DB_MANDY = libtcod.Color(217, 87, 99)
#DB_PLUM = libtcod.Color(215, 123, 186)
#DB_RAIN_FOREST = libtcod.Color(143, 151, 74)
#DB_STINGER = libtcod.Color(138, 111, 48)

LIGHT_ORANGE = palette.LIGHT_ORANGE
LIGHT_GREEN = palette.LIGHT_GREEN
LIGHT_BLUE = palette.LIGHT_BLUE
LIGHT_PINK = palette.LIGHT_PINK
RED = palette.RED
RED_D = palette.RED_D
ORANGE = palette.ORANGE
ORANGE_D = palette.ORANGE_D
YELLOW = palette.YELLOW
YELLOW_D = palette.YELLOW_D
GREEN = palette.GREEN
GREEN_D = palette.GREEN_D
CYAN = palette.CYAN
CYAN_D = palette.CYAN_D
BLUE = palette.BLUE
BLUE_D = palette.BLUE_D
PURPLE = palette.PURPLE
PURPLE_D = palette.PURPLE_D
PINK = palette.PINK
PINK_D = palette.PINK_D
DARK_BROWN = palette.DARK_BROWN
DARK_GREEN = palette.DARK_GREEN
DARK_BLUE = palette.DARK_BLUE
DARK_PURPLE = palette.DARK_PURPLE
WHITE = palette.WHITE
GRAY = palette.GRAY
GRAY_D = palette.GRAY_D
BLACK = palette.BLACK

################################
# Color Assignments
################################

UNINITIALIZED_BG = LIGHT_PINK
UNINITIALIZED_FG = DARK_PURPLE

UNSEEN_BG = BLACK
UNSEEN_FG = BLUE_D

FLOOR_BG = DARK_BROWN
FLOOR_FG = ORANGE_D

WALL_FG = GRAY_D

WATER_BG = BLUE_D
WATER_FG = CYAN_D

TEXT_SELECTED = WHITE
TEXT_UNSELECTED = GRAY

TEXT_ACTIVE = WHITE
TEXT_INACTIVE = GRAY_D
TEXT_NEW = WHITE
TEXT_OLD = GRAY

INTERFACE_BG = DARK_BLUE
INTERFACE_FG = GRAY_D
INACTIVE_GAME_FG = GRAY_D

HP_BAR_FULL = RED
HP_BAR_EMPTY = PURPLE_D

INVENTORY_HEADING = ORANGE
CURSOR = YELLOW
PATH = WHITE
BLOCKED_PATH = RED
