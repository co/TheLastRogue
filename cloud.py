from actor import Actor
from attacker import DamageTypes
import colors
from compositecommon import EntityShareTileEffect
from compositecore import Composite
import direction
from entityeffect import UndodgeableDamagAndBlockSameEffect, AddSpoofChild
import gametime
import geometry
from graphic import CharPrinter, GraphicChar
import messenger
from mover import Mover
from position import Position, DungeonLevel
import rng
from stats import DataTypes, DataPoint, GamePieceTypes, DataPointBonusSpoof
from text import Description
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
    steam.set_child(DataPoint(DataTypes.NEW_CLOUD_FUNCTION, new_steam_cloud))
    return steam


def new_dust_cloud(density):
    cloud = Composite()
    set_cloud_components(cloud, density)
    cloud.graphic_char.color_fg = colors.LIGHT_ORANGE
    cloud.set_child(CloudActor())
    cloud.set_child(DataPoint(DataTypes.NEW_CLOUD_FUNCTION, new_dust_cloud))
    cloud.set_child(DustLowerHitOfEntityShareTileEffect())
    cloud.set_child(CloudChangeAppearanceShareTileEffect())
    return cloud


def new_explosion_cloud(density):
    explosion = Composite()
    set_cloud_components(explosion, density)
    explosion.graphic_char.color_fg = colors.YELLOW
    explosion.set_child(Description("Explosion", "Don't go near it."))
    explosion.set_child(DisappearCloudActor())
    explosion.set_child(ExplosionDamageShareTileEffect())
    explosion.set_child(DataPoint(DataTypes.NEW_CLOUD_FUNCTION, new_explosion_cloud))
    return explosion


def new_fire_cloud(density):
    fire = Composite()
    set_cloud_components(fire, density)
    fire.graphic_char.icon = 'W'
    fire.graphic_char.color_fg = colors.RED
    fire.set_child(Description("Fire", "Don't get burnt."))
    fire.set_child(DisappearCloudActor())
    fire.set_child(FireDamageShareTileEffect())
    fire.set_child(DataPoint(DataTypes.NEW_CLOUD_FUNCTION, new_explosion_cloud))
    return fire


class FireDamageShareTileEffect(EntityShareTileEffect):
    def __init__(self):
        super(FireDamageShareTileEffect, self).__init__()
        self.component_type = "fire_damage_share_tile_effect"
        self.damage_types = [DamageTypes.FIRE]

    def _effect(self, **kwargs):
        target_entity = kwargs["target_entity"]
        source_entity = kwargs["source_entity"]
        damage_mid = 3
        damage_var = 6
        damage = rng.random_variance(damage_mid, damage_var)
        if not target_entity.has("effect_queue"):
            return

        damage_effect = UndodgeableDamagAndBlockSameEffect(source_entity, damage, self.damage_types,
                                                           messenger.HURT_BY_FIRE, "fire_damage",
                                                           time_to_live=gametime.single_turn)
        target_entity.effect_queue.add(damage_effect)


class AddSpoofChildShareEntityEffect(EntityShareTileEffect):
    def __init__(self):
        super(AddSpoofChildShareEntityEffect, self).__init__()
        self.spoof_child_creator = None

    def _effect(self, **kwargs):
        target_entity = kwargs["target_entity"]
        if not target_entity.has("effect_queue"):
            return
        if not self.spoof_child_creator:
            raise Exception("Spoof child not implemented")
        target_entity.effect_queue.add(AddSpoofChild(self.parent, self.spoof_child_creator(), 1))


class CloudChangeAppearanceShareTileEffect(AddSpoofChildShareEntityEffect):
    def __init__(self):
        super(CloudChangeAppearanceShareTileEffect, self).__init__()
        self.component_type = "cloud_change_appearance_share_tile_effect"
        self.spoof_child_creator = lambda: GraphicChar(self.parent.graphic_char.color_fg, colors.GRAY_D, None)


class DustLowerHitOfEntityShareTileEffect(AddSpoofChildShareEntityEffect):
    def __init__(self):
        super(DustLowerHitOfEntityShareTileEffect, self).__init__()
        self.component_type = "dust_lower_hit_of_entity_share_tile_effect"
        self.spoof_child_creator = lambda: DataPointBonusSpoof("hit", -10)


class ExplosionDamageShareTileEffect(EntityShareTileEffect):
    def __init__(self):
        super(ExplosionDamageShareTileEffect, self).__init__()
        self.component_type = "explosion_damage_share_tile_effect"

    def _effect(self, **kwargs):
        target_entity = kwargs["target_entity"]
        source_entity = kwargs["source_entity"]
        damage_mid = 20
        damage_var = 10
        damage = rng.random_variance(damage_mid, damage_var)
        if not target_entity.has("effect_queue"):
            return

        damage_effect = UndodgeableDamagAndBlockSameEffect(source_entity, damage, [DamageTypes.PHYSICAL],
                                                           messenger.HURT_BY_EXPLOSION, "explosion_damage",
                                                           time_to_live=gametime.single_turn)
        target_entity.effect_queue.add(damage_effect)


class DisappearCloudActor(Actor):
    def __init__(self):
        super(DisappearCloudActor, self).__init__()
        self.energy = -gametime.single_turn

    def tick(self):
        self.energy += self.energy_recovery
        while self.energy > 0:
            self.energy -= self.act()
        turn.current_turn += 1

    def act(self):
        self.parent.density.value -= 1
        if self.parent.density.value <= 0:
            self.parent.mover.try_remove_from_dungeon()
        return gametime.single_turn


class CloudActor(Actor):
    def __init__(self):
        super(CloudActor, self).__init__()
        self.energy = -gametime.normal_energy_gain

    def _float_to_position(self, position, density):
        original_cloud = self.parent.dungeon_level.value.get_tile_or_unknown(position).get_first_cloud()
        if original_cloud is None:
            new_cloud = self.parent.new_cloud_function.value(density)
            new_cloud.mover.replace_move(position, self.parent.dungeon_level.value)
        else:
            original_cloud.density.value += density
        self.parent.density.value -= density

    def tick(self):
        self.energy += self.energy_recovery
        while self.energy > 0:
            self.energy -= self.act()
        turn.current_turn += 1

    def act(self):
        self.spread()
        return gametime.single_turn

    def spread(self):
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
