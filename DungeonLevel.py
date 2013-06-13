import Terrain
import libtcodpy as libtcod


def charToTerrain(c, position):
    if(c == '#'):
        return Terrain.Wall(position)
    elif(c == '+'):
        return Terrain.Door(position, False)
    elif(c == '~'):
        return Terrain.Water(position)
    elif(c == ' '):
        return Terrain.Floor(position)


def read_file(file_name):
    f = open(file_name, "r")
    data = f.readlines()
    data = [line.strip() for line in data]
    f.close()
    return data


class DungeonLevel(object):

    #def __init__(self, TerrainMatrix):
        #self.TerrainMatrix = TerrainMatrix

    def __init__(self):
        dungeon = read_file("test.level")
        self.width = len(dungeon[0])
        self.height = len(dungeon)

        self.terrainMatrix = [[charToTerrain(dungeon[y][x], (x, y))
                              for x in range(self.width)]
                              for y in range(self.height)]

    def Draw(self, playerPosition):
        fovRadius = 5
        self.UpdateCalculateDungeonPropertyMap()
        libtcod.map_compute_fov(self.fovMap,
                                playerPosition.x, playerPosition.y,
                                fovRadius, True)
        for y, row in enumerate(self.terrainMatrix):
            for x, tile in enumerate(row):
                tile.Draw(libtcod.map_is_in_fov(self.fovMap, x, y))

    def isTilePassable(self, position):
        return not self.terrainMatrix[position.y][position.x].IsSolid()

    def UpdateCalculateDungeonPropertyMap(self):
        self.fovMap = libtcod.map_new(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                tile = self.terrainMatrix[y][x]
                libtcod.map_set_properties(self.fovMap, x, y,
                                           tile.IsTransparent(),
                                           tile.IsSolid())
