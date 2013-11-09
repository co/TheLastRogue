from action import Action, SOURCE_ENTITY, GAME_STATE
from compositecore import Leaf
import gametime
import geometry
import libtcodpy as libtcod
import shoot
import animation
import colors
import symbol


class PlayerMissileAction(Action):
    def act(self, **kwargs):
        source_entity = kwargs[SOURCE_ENTITY]
        game_state = kwargs[GAME_STATE]
        max_missile_distance =\
            self.max_missile_distance(source_entity=source_entity)
        path = shoot.player_select_missile_path(source_entity,
                                                max_missile_distance,
                                                game_state)

        if path is None or path[-1] == source_entity.position.value:
            return False
        dungeon_level = source_entity.dungeon_level.value
        hit_detector = shoot.MissileHitDetection(False, False)
        path_taken = hit_detector.get_path_taken(path, dungeon_level)
        if path_taken is None or len(path_taken) < 1:
            return False
        self.send_missile(dungeon_level, path_taken, game_state, source_entity)
        self.add_energy_spent_to_entity(source_entity)

    def max_missile_distance(self, **kwargs):
        pass

    def send_missile(self, dungeon_level, path, game_state, source_entity):
        pass


def animate_flight(game_state, path, symbol_char, color_fg):
    flight_animation =\
        animation.MissileAnimation(game_state, symbol_char, color_fg, path)
    flight_animation.run_animation()


class PlayerThrowItemAction(PlayerMissileAction):
    """
    This action will prompt the player to throw the parent item.
    """
    def __init__(self):
        super(PlayerThrowItemAction, self).__init__()
        self.component_type = "action"
        self.name = "Throw"
        self.display_order = 95

    def max_missile_distance(self, **kwargs):
        """
        The distance the item can be thrown by the player.
        """
        source_entity = kwargs[SOURCE_ENTITY]
        return source_entity.strength.value * 4 - self.parent.weight.value

    def remove_from_inventory(self, source_entity):
        """
        Removes the parent item from the inventory.
        """
        source_entity.inventory.remove_item(self.parent)

    def send_missile(self, dungeon_level, path, game_state, source_entity):
        """
        The final step of the throw.
        """
        self.remove_from_inventory(source_entity)
        animate_flight(game_state, path, self.parent.graphic_char.symbol,
                       self.parent.graphic_char.color_fg)
        self.parent.thrower.throw_effect(dungeon_level, path[-1])


class PlayerThrowRockAction(PlayerMissileAction):
    def __init__(self):
        super(PlayerThrowRockAction, self).__init__()
        self.name = "Throw Rock"
        self.display_order = 95
        self.symbol = symbol.BIG_CENTER_DOT
        self.color_fg = colors.GRAY
        self.energy_cost = gametime.double_turn

    def send_missile(self, dungeon_level, path, game_state, source_entity):
        animate_flight(game_state, path, self.symbol, self.color_fg)
        rock_hit_position(dungeon_level, path[-1], source_entity)

    def can_act(self, **kwargs):
        return True

    def max_missile_distance(self, **kwargs):
        source_entity = kwargs[SOURCE_ENTITY]
        return max_throw_distance(source_entity.strength.value)


def rock_hit_position(dungeon_level, position, source_entity):
    target_entity = dungeon_level.get_tile(position).get_first_entity()
    if target_entity is None:
        return
    source_entity.attacker.throw_rock_damage_entity(target_entity)


def max_throw_distance(strength):
    return strength + 1


class PlayerShootWeaponAction(PlayerMissileAction):
    def __init__(self, ranged_weapon):
        super(PlayerShootWeaponAction, self).__init__()
        self.name = "Shoot"
        self.display_order = 85
        self.symbol = symbol.BIG_CENTER_DOT
        self.ranged_weapon = ranged_weapon
        self.color_fg = colors.WHITE

    def send_missile(self, dungeon_level, path, game_state, source_entity):
        animate_flight(game_state, path, self.symbol, self.color_fg)
        self.hit_position(dungeon_level, path[-1], source_entity)

    def can_act(self, **kwargs):
        return True

    def hit_position(self, dungeon_level, position, source_entity):
        target_entity = dungeon_level.get_tile(position).get_first_entity()
        if target_entity is None:
            return
        self.ranged_weapon.damage_provider.damage_entity(source_entity,
                                                         target_entity)

    def max_missile_distance(self, **kwargs):
        return self.ranged_weapon.weapon_range.value


class MonsterThrowRockAction(Leaf):
    def __init__(self):
        super(MonsterThrowRockAction, self).__init__()
        self.component_type = "monster_range_attack_action"
        self.symbol = symbol.BIG_CENTER_DOT
        self.color_fg = colors.GRAY

    def act(self, destination):
        path = self._get_path(destination)
        if path is None or path[-1] == self.parent.position.value:
            return False
        dungeon_level = self.parent.dungeon_level.value
        hit_detector = shoot.MissileHitDetection(False, False)
        path_taken = hit_detector.get_path_taken(path, dungeon_level)
        if path_taken is None or len(path_taken) < 1:
            return False
        self.send_missile(dungeon_level, path_taken)
        return True

    def _get_path(self, destination):
        result = []
        sx, sy = self.parent.position.value
        dx, dy = destination
        libtcod.line_init(sx, sy, dx, dy)
        x, y = libtcod.line_step()
        while not x is None:
            result.append((x, y))
            x, y = libtcod.line_step()
        result.append(destination)
        return result

    def is_destination_within_range(self, destination):
        return (1 < geometry.chess_distance(self.parent.position.value, destination) <=
                max_throw_distance(self.parent.strength.value))

    def is_something_blocking(self, destination):
        path = self._get_path(destination)
        hit_detector = shoot.MissileHitDetection(False, False)
        dungeon_level = self.parent.dungeon_level.value
        path_taken = hit_detector.get_path_taken(path, dungeon_level)
        return geometry.chess_distance(self.parent.position.value, destination) != len(path_taken)

    def send_missile(self, dungeon_level, path):
        animate_flight(self.parent.game_state.value, path, self.symbol, self.color_fg)
        rock_hit_position(dungeon_level, path[-1], self.parent)
