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
