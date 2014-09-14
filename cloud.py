import random
from Status import StatusDescription, FIRE_STATUS_DESCRIPTION
from actor import Actor
from attacker import DamageTypes
import colors
from compositecommon import EntityShareTileEffect, PoisonEntityEffectFactory
from compositecore import Composite
import direction
from entityeffect import UndodgeableDamagAndBlockSameEffect, AddSpoofChild
import gametime
import geometry
from graphic import CharPrinter, GraphicChar
import icon
import messenger
from mover import Mover
from position import Position, DungeonLevel
import rng
from stats import DataTypes, DataPoint, GamePieceTypes, DataPointBonusSpoof
from statusflags import StatusFlags
from text import Description
import turn


class CloudTypes:
    EXPLOSION = "explosion"
    STEAM = "steam"
    FIRE = "fire"
    DUST = "dust"
    POISON = "poison"


def set_cloud_components(game_state, cloud, density):
    cloud.set_child(DataPoint(DataTypes.ENERGY, -gametime.single_turn))
    cloud.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.CLOUD))
    cloud.set_child(DataPoint(DataTypes.GAME_STATE, game_state))
    cloud.set_child(CharPrinter())
    cloud.set_child(Position())
    cloud.set_child(DungeonLevel())
    cloud.set_child(Mover())
    cloud.set_child(GraphicChar(None, None, 178))
    cloud.set_child(DataPoint(DataTypes.DENSITY, density))
    cloud.set_child(StatusFlags([StatusFlags.FLYING]))


def new_steam_cloud(game_state, density):
    cloud = Composite()
    set_cloud_components(game_state, cloud, density)
    cloud.graphic_char.color_fg = colors.WHITE
    cloud.set_child(CloudActor())
    cloud.set_child(DataPoint(DataTypes.CLONE_FUNCTION, new_steam_cloud))
    cloud.set_child(DataPoint(DataTypes.CLOUD_TYPE, CloudTypes.STEAM))
    cloud.set_child(CloudChangeAppearanceShareTileEffect())
    return cloud


def new_poison_cloud(game_state, density):
    cloud = Composite()
    set_cloud_components(game_state, cloud, density)
    cloud.graphic_char.color_fg = colors.GREEN
    cloud.set_child(CloudActor())
    cloud.set_child(DataPoint(DataTypes.CLONE_FUNCTION, new_poison_cloud))
    cloud.set_child(DataPoint(DataTypes.CLOUD_TYPE, CloudTypes.POISON))
    cloud.set_child(PoisonCloudShareTileEffect())
    cloud.set_child(CloudChangeAppearanceShareTileEffect())
    return cloud


def new_dust_cloud(game_state, density):
    cloud = Composite()
    set_cloud_components(game_state, cloud, density)
    cloud.graphic_char.color_fg = colors.LIGHT_ORANGE
    cloud.set_child(CloudActor())
    cloud.set_child(DataPoint(DataTypes.CLONE_FUNCTION, new_dust_cloud))
    cloud.set_child(DustLowerHitOfEntityShareTileEffect())
    cloud.set_child(CloudChangeAppearanceShareTileEffect())
    cloud.set_child(DataPoint(DataTypes.CLOUD_TYPE, CloudTypes.DUST))
    return cloud


def new_explosion_cloud(game_state, density):
    explosion = Composite()
    set_cloud_components(game_state, explosion, density)
    explosion.graphic_char.color_fg = colors.YELLOW
    explosion.set_child(Description("Explosion", "Don't go near it."))
    explosion.set_child(DisappearCloudActor())
    explosion.set_child(ExplosionDamageShareTileEffect())
    explosion.set_child(DataPoint(DataTypes.CLONE_FUNCTION, new_explosion_cloud))
    explosion.set_child(DataPoint(DataTypes.CLOUD_TYPE, CloudTypes.EXPLOSION))
    explosion.set_child(CloudChangeAppearanceShareTileEffect())
    return explosion


def set_non_flying_cloud_components(cloud):
    cloud.set_child(StatusFlags([]))


def new_fire_cloud(game_state, density):
    fire = Composite()
    set_cloud_components(game_state, fire, density)
    set_non_flying_cloud_components(fire)
    fire.graphic_char.icon = icon.FIRE
    fire.graphic_char.color_fg = colors.RED
    fire.set_child(Description("Fire", "Don't get burnt."))
    fire.set_child(DisappearCloudActor())
    fire.set_child(FireDamageShareTileEffect())
    fire.set_child(DataPoint(DataTypes.CLONE_FUNCTION, new_explosion_cloud))
    fire.set_child(DataPoint(DataTypes.CLOUD_TYPE, CloudTypes.FIRE))
    fire.set_child(CloudChangeAppearanceShareTileEffect())
    return fire


class FireDamageShareTileEffect(EntityShareTileEffect):
    def __init__(self):
        super(FireDamageShareTileEffect, self).__init__()
        self.component_type = "fire_damage_share_tile_effect"
        self.damage_types = [DamageTypes.FIRE]

    def effect(self, **kwargs):
        target_entity = kwargs["target_entity"]
        source_entity = kwargs["source_entity"]
        damage_mid = 5
        damage_var = 3
        damage = rng.random_variance(damage_mid, damage_var)
        if not target_entity.has("effect_queue"):
            return
        damage_effect = UndodgeableDamagAndBlockSameEffect(source_entity, damage, self.damage_types,
                                                           messenger.HURT_BY_FIRE, "fire_damage",
                                                           time_to_live=gametime.single_turn,
                                                           status_icon=FIRE_STATUS_DESCRIPTION)
        target_entity.effect_queue.add(damage_effect)


class AddEntityEffectShareTile(EntityShareTileEffect):
    """
    Abstract subclasses should define entity effect.
    """
    def __init__(self):
        super(AddEntityEffectShareTile, self).__init__()

    def effect(self, **kwargs):
        target_entity = kwargs["target_entity"]
        if not target_entity.has("effect_queue"):
            return
        target_entity.effect_queue.add(self.entity_effect)


class AddSpoofChildShareEntityEffect(EntityShareTileEffect):
    def __init__(self):
        super(AddSpoofChildShareEntityEffect, self).__init__()

    def effect(self, **kwargs):
        target_entity = kwargs["target_entity"]
        if not target_entity.has("effect_queue"):
            return
        target_entity.effect_queue.add(AddSpoofChild(self.parent, self.spoof_child_factory(), 1))

    def spoof_child_factory(self):
        pass


class CloudChangeAppearanceShareTileEffect(AddSpoofChildShareEntityEffect):
    def __init__(self):
        super(CloudChangeAppearanceShareTileEffect, self).__init__()
        self.component_type = "cloud_change_appearance_share_tile_effect"

    def spoof_child_factory(self):
        return GraphicChar(self.parent.graphic_char.color_fg, colors.GRAY_D, None)


class DustLowerHitOfEntityShareTileEffect(AddSpoofChildShareEntityEffect):
    def __init__(self):
        super(DustLowerHitOfEntityShareTileEffect, self).__init__()
        self.component_type = "dust_lower_hit_of_entity_share_tile_effect"

    def spoof_child_factory(self):
        return DataPointBonusSpoof("hit", -10)


class PoisonCloudShareTileEffect(AddEntityEffectShareTile):
    def __init__(self):
        super(PoisonCloudShareTileEffect, self).__init__()
        self.component_type = "poison_share_tile_effect"
        self.poison_effect_factory = PoisonEntityEffectFactory(None, random.randrange(8, 14), 2, random.randrange(10, 20))

    @property
    def entity_effect(self):
        return self.poison_effect_factory()


class ExplosionDamageShareTileEffect(EntityShareTileEffect):
    def __init__(self):
        super(ExplosionDamageShareTileEffect, self).__init__()
        self.component_type = "explosion_damage_share_tile_effect"

    def effect(self, **kwargs):
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

    def tick(self):
        self.parent.energy.value += self.energy_recovery
        while self.parent.energy.value > 0:
            self.parent.energy.value -= self.act()
        turn.current_turn += 1

    def act(self):
        self.parent.density.value -= 1
        if self.parent.density.value <= 0:
            self.parent.mover.try_remove_from_dungeon()
        return gametime.single_turn


class CloudActor(Actor):
    def __init__(self):
        super(CloudActor, self).__init__()

    def _float_to_position(self, position, density):
        original_cloud = self.parent.dungeon_level.value.get_tile_or_unknown(position).get_first_cloud()
        if original_cloud is None:
            new_cloud = self.parent.clone_function.value(self.parent.game_state.value, density)
            new_cloud.mover.try_move(position, self.parent.dungeon_level.value)
            self.parent.density.value -= density
        elif original_cloud.cloud_type.value == self.parent.cloud_type.value:
            original_cloud.density.value += density
            self.parent.density.value -= density

    def tick(self):
        self.parent.energy.value += self.energy_recovery
        while self.parent.energy.value > 0:
            self.parent.energy.value -= self.act()
        turn.current_turn += 1

    def act(self):
        self.spread()
        return gametime.single_turn

    def spread(self):
        minimal_cloud_size = 2
        if self.parent.density.value < minimal_cloud_size:
            self.parent.mover.try_remove_from_dungeon()
            return gametime.single_turn
        density_per_tile = max(self.parent.density.value / 4, 1)
        neighbours = [geometry.add_2d(offset, self.parent.position.value) for offset in direction.AXIS_DIRECTIONS]
        random.shuffle(neighbours)
        for neighbour in neighbours:
            self._float_to_position(neighbour, density_per_tile)
            if self.parent.density.value < density_per_tile:
                break
            if self.parent.density.value < minimal_cloud_size:
                break
