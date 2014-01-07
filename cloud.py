from actor import Actor
import colors
from compositecore import Composite
import direction
import gametime
import geometry
from graphic import CharPrinter, GraphicChar
from mover import Mover
from position import Position, DungeonLevel
import rng
from stats import DataTypes, DataPoint, GamePieceTypes
import turn


def set_cloud_components(cloud, density):
    cloud.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.CLOUD))
    cloud.set_child(CharPrinter())
    cloud.set_child(Position())
    cloud.set_child(DungeonLevel())
    cloud.set_child(Mover())
    cloud.set_child(GraphicChar(None, None, 178))
    cloud.set_child(DataPoint(DataTypes.DENSITY, density))


def new_steam_cloud(density):
    steam = Composite()
    set_cloud_components(steam, density)
    steam.graphic_char.color_fg = colors.WHITE
    steam.set_child(CloudActor())
    return steam


class CloudActor(Actor):
    def __init__(self):
        super(CloudActor, self).__init__()

    def _float_to_position(self, position, density):
        original_cloud = self.parent.dungeon_level.value.get_tile_or_unknown(position).get_first_cloud()
        if original_cloud is None:
            new_cloud = new_steam_cloud(density)
            new_cloud.mover.try_move(position, self.parent.dungeon_level.value)
        else:
            original_cloud.density.value += density
        self.parent.density.value -= density

    def tick(self):
        self.energy += self.energy_recovery
        while self.energy > 0:
            self.energy -= self.act()
        turn.current_turn += 1

    def act(self):
        if self.parent.density.value < 2:
            self.parent.mover.try_remove_from_dungeon()
            return gametime.single_turn

        density_per_tile = max(self.parent.density.value / 4, 1)
        neighbours = [geometry.add_2d(offset, self.parent.position.value) for offset in direction.AXIS_DIRECTIONS]
        for neighbour in neighbours:
            if not (rng.coin_flip() and rng.coin_flip()):
                self._float_to_position(neighbour, density_per_tile)
            if self.parent.density.value < density_per_tile:
                break
        return gametime.single_turn

#class Cloud(actor.Actor):
#    def __init__(self, density):
#        super(Cloud, self).__init__()
#        self.energy = 0
#        self.energy_recovery = gametime.normal_energy_gain
#        self.piece_type = gamepiece.GamePieceType.CLOUD
#        self.max_instances_in_single_tile = 1
#        self.density = density
#        self.gfx_char.symbol = 178
#        self.gfx_char.color_fg = colors.WHITE
#
#    def act(self):
#        return 0
#
#    def piece_copy(self, copy=None):
#        if(copy is None):
#            copy = self.__class__(self.density)
#        return super(Cloud, self).piece_copy(copy)
#
#
#class Steam(Cloud):
#    def __init__(self, density):
#        super(Steam, self).__init__(density)
#
#    def _float_to_position(self, position, density_of_gust):
#        original_cloud =\
#            self.dungeon_level.get_tile_or_unknown(position).get_first_cloud()
#        if(original_cloud is None):
#            new_cloud = Steam(density_of_gust)
#            new_cloud.try_move(position, self.dungeon_level)
#        else:
#            original_cloud.density += density_of_gust
#        self.density -= density_of_gust
#
#    def act(self):
#        if(self.density < 2):
#            self.try_remove_from_dungeon()
#            return gametime.single_turn
#
#        density_per_gust = max(self.density / 5, 1)
#        neighbours = [geo.add_2d(offset, self.position)
#                      for offset in direction.AXIS_DIRECTIONS]
#        for neighbour in neighbours:
#            if not (rng.coin_flip() and rng.coin_flip()):
#                self._float_to_position(neighbour, density_per_gust)
#            if self.density < density_per_gust:
#                break
#        return gametime.single_turn
