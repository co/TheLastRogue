from action import Action, SOURCE_ENTITY, GAME_STATE
import shoot
import animation
import colors


class PlayerMissileAction(Action):
    def act(self, **kwargs):
        source_entity = kwargs[SOURCE_ENTITY]
        game_state = kwargs[GAME_STATE]
        max_throw_distance =\
            self.max_throw_distance(source_entity=source_entity)
        path = shoot.player_select_missile_path(source_entity,
                                                max_throw_distance,
                                                game_state)

        if(path is None or path[-1] == source_entity.position):
            return False
        dungeon_level = source_entity.dungeon_level.value
        hit_detector = shoot.MissileHitDetection(False, False)
        path_taken = hit_detector.get_path_taken(path, dungeon_level)
        self.send_missile(dungeon_level, path_taken, game_state, source_entity)
        self.add_energy_spent_to_entity(source_entity)

    def max_throw_distance(self, **kwargs):
        pass

    def send_missile(self, dungeon_level, path, game_state, source_entity):
        pass

    def animate_flight(self, game_state, path, symbol, color_fg):
        flight_animation =\
            animation.MissileAnimation(game_state, symbol, color_fg, path)
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

    def max_throw_distance(self, **kwargs):
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
        print self.parent
        self.animate_flight(game_state, path, self.parent.graphic_char.symbol,
                            self.parent.graphic_char.color_fg)
        self.parent.thrower.throw_effect(dungeon_level, path[-1])


class PlayerThrowRockAction(PlayerMissileAction):
    def __init__(self):
        super(PlayerThrowRockAction, self).__init__()
        self.name = "Throw Rock"
        self.display_order = 95
        self.symbol = 249
        self.color_fg = colors.GRAY

    def send_missile(self, dungeon_level, path, game_state, source_entity):
        self.animate_flight(game_state, path, self.symbol, self.color_fg)
        self.hit_position(dungeon_level, path[-1], source_entity)

    def can_act(self, **kwargs):
        return True

    def hit_position(self, dungeon_level, position, source_entity):
        target_entity = dungeon_level.get_tile(position).get_first_entity()
        if(target_entity is None):
            return
        source_entity.rock_throwing_damage().damage_entity(source_entity,
                                                           target_entity)

    def max_throw_distance(self, **kwargs):
        source_entity = kwargs[SOURCE_ENTITY]
        return source_entity.strength.value + 1


class PlayerShootWeaponAction(PlayerMissileAction):
    def __init__(self, source_item):
        super(PlayerShootWeaponAction, self).__init__()
        self.name = "Shoot"
        self.display_order = 85
        self.symbol = '.'
        self.color_fg = colors.WHITE

    def send_missile(self, dungeon_level, path, game_state, source_entity):
        self.animate_flight(game_state, path, self.symbol, self.color_fg)
        self.hit_position(dungeon_level, path[-1], source_entity)

    def can_act(self, **kwargs):
        return True

    def hit_position(self, dungeon_level, position, source_entity):
        target_entity = dungeon_level.get_tile(position).get_first_entity()
        if(target_entity is None):
            return
        self.parent.damage.damage_entity(source_entity, target_entity)

    def max_throw_distance(self, **kwargs):
        return self.parent.weapon_range.value
