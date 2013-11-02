import terrain
import tile
from dungeonlevel import DungeonLevel


def get_empty_tile_matrix(width, height):
    return [[tile.Tile()
             for x in range(width)]
            for y in range(height)]


def unknown_level_map(width, height, depth):
    tile_matrix = get_empty_tile_matrix(width, height)
    dungeon_level = DungeonLevel(tile_matrix, depth)
    for x in range(width):
        for y in range(height):
            unknown_terrain = terrain.Unknown()
            unknown_terrain.mover.replace_move((x, y), dungeon_level)
    return dungeon_level


def dungeon_level_from_lines(lines):
    terrain_matrix = terrain_matrix_from_lines(lines)
    dungeon_level = DungeonLevel(terrain_matrix, 1)
    set_terrain_from_lines(dungeon_level, lines)
    return dungeon_level


def dungeon_level_from_file(file_name):
    lines = read_file(file_name)
    return dungeon_level_from_lines(lines)


def terrain_matrix_from_lines(lines):
    width = len(lines[0])
    height = len(lines)
    terrain_matrix = get_empty_tile_matrix(width, height)
    return terrain_matrix


def set_terrain_from_lines(dungeon_level, lines):
        for x in range(dungeon_level.width):
            for y in range(dungeon_level.height):
                terrain = char_to_terrain(lines[y][x])
                terrain.mover.replace_move((x, y), dungeon_level)


def char_to_terrain(c):
    if(c == '#'):
        return terrain.Wall()
    elif(c == '+'):
        return terrain.Door()
    elif(c == '~'):
        return terrain.Water()
    elif(c == 'g'):
        return terrain.GlassWall()
    else:
        return terrain.Floor()


def read_file(file_name):
    f = open(file_name, "r")
    data = f.readlines()
    data = [line.strip() for line in data]
    f.close()
    return data
