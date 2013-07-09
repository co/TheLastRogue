import libtcodpy as libtcod


################################
# Color definitions
################################

HOT_PINK = libtcod.Color(255, 0, 102)
BLACK = libtcod.Color(0, 0, 0)
WHITE = libtcod.Color(255, 255, 255)

DARK_SAND_STONE = libtcod.Color(117, 97, 74)
LIGHT_SAND_STONE = libtcod.Color(193, 159, 119)

COLD_GRAY = libtcod.Color(98, 92, 99)
COLD_GREEN = libtcod.Color(153, 170, 158)

PURPLE_SHADOW_LIGHT = libtcod.Color(105, 100, 117)
PURPLE_SHADOW_DARK = libtcod.Color(144, 140, 154)


DARK = libtcod.Color(50, 56, 56)

DARK_WALL = libtcod.Color(0, 0, 100)
LIGHT_WALL = libtcod.Color(130, 110, 50)
DARK_GROUND = libtcod.Color(50, 50, 150)
LIGHT_GROUND = libtcod.Color(200, 180, 50)

# DawnBringer 16 Palette.
DB1 = libtcod.Color(20, 12, 28)
DB2 = libtcod.Color(68, 36, 52)
DB3 = libtcod.Color(48, 52, 109)
DB4 = libtcod.Color(78, 74, 78)
DB5 = libtcod.Color(133, 76, 48)
DB6 = libtcod.Color(52, 101, 36)
DB7 = libtcod.Color(208, 70, 72)
DB8 = libtcod.Color(117, 113, 97)
DB9 = libtcod.Color(89, 125, 206)
DB10 = libtcod.Color(210, 125, 44)
DB11 = libtcod.Color(133, 149, 161)
DB12 = libtcod.Color(109, 170, 44)
DB13 = libtcod.Color(210, 170, 153)
DB14 = libtcod.Color(109, 194, 202)
DB15 = libtcod.Color(218, 212, 94)
DB16 = libtcod.Color(222, 238, 214)

# DawnBringer 32 Palette.
DB_BLACK = libtcod.Color(0, 0, 0)
DB_VALHALLA = libtcod.Color(34, 32, 52)
DB_LOULOU = libtcod.Color(69, 40, 60)
DB_OILED_CEDAR = libtcod.Color(102, 57, 49)
DB_ROPE = libtcod.Color(143, 86, 59)
DB_TAHITI_GOLD = libtcod.Color(223, 113, 38)
DB_TWINE = libtcod.Color(217, 160, 102)
DB_PANCHO = libtcod.Color(238, 195, 154)

DB_GOLDEN_FIZZ = libtcod.Color(251, 242, 54)
DB_ATLANTIS = libtcod.Color(153, 229, 80)
DB_CHRISTI = libtcod.Color(106, 190, 48)
DB_ELF_GREEN = libtcod.Color(55, 148, 110)
DB_DELL = libtcod.Color(75, 105, 47)
DB_VERDIGRIS = libtcod.Color(82, 75, 36)
DB_OPAL = libtcod.Color(50, 60, 57)
DB_DEEP_KOAMARU = libtcod.Color(63, 63, 116)

DB_VENICE_BLUE = libtcod.Color(48, 96, 130)
DB_ROYAL_BLUE = libtcod.Color(91, 110, 225)
DB_CORNFLOWER = libtcod.Color(99, 155, 255)
DB_VIKING = libtcod.Color(95, 205, 228)
DB_LIGHT_STEEL_BLUE = libtcod.Color(203, 219, 252)
DB_WHITE = libtcod.Color(255, 255, 255)
DB_HEATHER = libtcod.Color(155, 173, 183)
DB_TOPAZ = libtcod.Color(132, 126, 135)

DB_DIM_GRAY = libtcod.Color(105, 106, 106)
DB_SMOKEY_ASH = libtcod.Color(89, 86, 82)
DB_CLAIRVOYANT = libtcod.Color(118, 66, 138)
DB_BROWN = libtcod.Color(172, 50, 50)
DB_MANDY = libtcod.Color(217, 87, 99)
DB_PLUM = libtcod.Color(215, 123, 186)
DB_RAIN_FOREST = libtcod.Color(143, 151, 74)
DB_STINGER = libtcod.Color(138, 111, 48)

################################
# Color Assignments
################################

UNINITIALIZED_BG = HOT_PINK
UNINITIALIZED_FG = WHITE

UNSEEN_BG = DB1
UNSEEN_FG = DB3

FLOOR_BG = DB4
FLOOR_FG = DB8

WALL_BG = DARK_SAND_STONE
WALL_FG = LIGHT_SAND_STONE

TEXT_SELECTED = DB_WHITE
TEXT_UNSELECTED = DB_TWINE

TEXT_ACTIVE = DB_WHITE
TEXT_INACTIVE = DB_TOPAZ
TEXT_NEW = DB_WHITE
TEXT_OLD = DB_TOPAZ

INTERFACE_BG = DB_BLACK

INVENTORY_HEADING = DB_TAHITI_GOLD
