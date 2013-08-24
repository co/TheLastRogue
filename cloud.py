import gamepiece
import actor
import colors
import direction
import geometry as geo
import gametime
import rng


class Cloud(actor.Actor):
    def __init__(self, density):
        super(Cloud, self).__init__()
        self.energy = 0
        self.energy_recovery = gametime.normal_energy_gain
        self.piece_type = gamepiece.GamePieceType.CLOUD
        self.max_instances_in_single_tile = 1
        self.density = density

    def act(self):
        return 0

    @property
    def symbol(self):
        return 178

    @property
    def color_fg(self):
        return colors.WHITE

    def piece_copy(self, copy=None):
        if(copy is None):
            copy = self.__class__(self.density)
        return super(Cloud, self).piece_copy(copy)


class Steam(Cloud):
    def __init__(self, density):
        super(Steam, self).__init__(density)

    def _float_to_position(self, position, density_of_gust):
        original_cloud =\
            self.dungeon_level.get_tile_or_unknown(position).get_first_cloud()
        if(original_cloud is None):
            new_cloud = Steam(density_of_gust)
            new_cloud.try_move(position, self.dungeon_level)
        else:
            original_cloud.density += density_of_gust
        self.density -= density_of_gust

    def act(self):
        if(self.density < 2):
            self.try_remove_from_dungeon()
            return gametime.single_turn

        density_per_gust = max(self.density / 5, 1)
        neighbours = [geo.add_2d(offset, self.position)
                      for offset in direction.AXIS_DIRECTIONS]
        for neighbour in neighbours:
            if not (rng.coin_flip() and rng.coin_flip()):
                self._float_to_position(neighbour, density_per_gust)
            if self.density < density_per_gust:
                break
        return gametime.single_turn
