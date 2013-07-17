import random
import colors
import shoot
import animation
import entityeffect

#  Arguments:
SOURCE_ENTITY = "source_entity"
TARGET_ENTITY = "target_entity"
GAME_STATE = "game_state"


class Action(object):
    def __init__(self):
        self.name = "XXX_Action_Name_XX"
        self.display_order = 100

    def act(self, **kwargs):
        pass

    def can_act(self, **kwargs):
        return True


class ItemAction(Action):
    def __init__(self, source_item):
        super(ItemAction, self).__init__()
        self.name = "XXX_Item_Action_Name_XXX"
        self.source_item = source_item

    def remove_from_inventory(self):
        self.source_item.inventory.remove_item(self.source_item)


class EquipAction(ItemAction):
    def __init__(self, source_item):
        super(EquipAction, self).__init__(source_item)
        self.name = "Equip"
        self.display_order = 90

    def act(self, **kwargs):
        target_entity = kwargs[TARGET_ENTITY]
        self.equip(target_entity)

    def can_act(self, **kwargs):
        target_entity = kwargs[TARGET_ENTITY]
        return target_entity.equipment.can_equip(self.source_item)

    def equip(self, target_entity):
        equip_effect = entityeffect.Equip(target_entity,
                                          target_entity, self.source_item)
        target_entity.add_entity_effect(equip_effect)
        self.remove_from_inventory()


class DrinkAction(ItemAction):
    def __init__(self, source_item):
        super(DrinkAction, self).__init__(source_item)
        self.name = "Drink"
        self.display_order = 90

    def act(self, **kwargs):
        target_entity = kwargs[TARGET_ENTITY]
        self.drink(target_entity)
        self.remove_from_inventory()
        return True

    def drink(self):
        pass


class HealingPotionDrink(DrinkAction):
    def __init__(self, source_item):
        super(HealingPotionDrink, self).__init__(source_item)
        self.min_health = 5
        self.max_health = 10

    def drink(self, target_entity):
        health = random.randrange(self.min_health, self.max_health)
        heal_effect = entityeffect.Heal(target_entity, target_entity, health)
        target_entity.add_entity_effect(heal_effect)


class DropAction(ItemAction):
    def __init__(self, source_item):
        super(DropAction, self).__init__(source_item)
        self.name = "Drop"
        self.display_order = 110

    def act(self, **kwargs):
        if(not self.source_item.inventory is None):
            drop_successful =\
                self.source_item.inventory.try_drop_item(self.source_item)
            return drop_successful
        return False


class DescendStairsAction(Action):
    def __init__(self):
        super(DescendStairsAction, self).__init__()
        self.name = "Descend Stairs"
        self.display_order = 50

    def act(self, **kwargs):
        target_entity = kwargs[TARGET_ENTITY]
        current_dungeon_level = target_entity.dungeon_level
        next_dungeon_level = current_dungeon_level.\
            dungeon.get_dungeon_level(current_dungeon_level.depth + 1)
        if(next_dungeon_level is None):
            return False
        destination_position = next_dungeon_level.up_stairs[0].position
        target_entity.try_move(destination_position, next_dungeon_level)


class PlayerMissileAction(Action):
    def act(self, **kwargs):
        source_entity = kwargs[SOURCE_ENTITY]
        game_state = kwargs[GAME_STATE]
        max_throw_distance = self.max_throw_distance(source_entity)
        path = shoot.player_select_missile_path(source_entity,
                                                max_throw_distance,
                                                game_state)

        if(path is None or path[-1] == source_entity.position):
            return False
        dungeon_level = source_entity.dungeon_level
        hit_detector = shoot.MissileHitDetection(False, False)
        path_taken = hit_detector.get_path_taken(path, dungeon_level)
        self.throw_path(dungeon_level, path_taken, game_state, source_entity)
        return True

    def throw_path(self, dungeon_level, path, game_state, source_entity):
        pass


class PlayerThrowItemAction(ItemAction, PlayerMissileAction):
    def __init__(self, source_item):
        super(PlayerThrowItemAction, self).__init__(source_item)
        self.name = "Throw"
        self.display_order = 95

    def max_throw_distance(self, source_entity):
        return source_entity.strength * 4 - self.source_item.weight

    def throw_path(self, dungeon_level, path, game_state, source_entity):
        self.remove_from_inventory()
        self.animate_flight(game_state, path)
        self.source_item.throw_effect(dungeon_level, path[-1])

    def animate_flight(self, game_state, path):
        flight_animation =\
            animation.MissileAnimation(game_state, self.source_item.symbol,
                                       self. source_item.color_fg, path)
        flight_animation.run_animation()


class PlayerThrowRockAction(PlayerMissileAction):
    def __init__(self):
        super(PlayerThrowRockAction, self).__init__()
        self.name = "Throw Rock"
        self.display_order = 95
        self.SYMBOL = 249
        self.COLOR_FG = colors.DB_TOPAZ

    def throw_path(self, dungeon_level, path, game_state, source_entity):
        self.animate_flight(game_state, path)
        self.hit_position(dungeon_level, path[-1], source_entity)

    def animate_flight(self, game_state, path):
        flight_animation =\
            animation.MissileAnimation(game_state, self.SYMBOL,
                                       self.COLOR_FG, path)
        flight_animation.run_animation()

    def can_act(self, **kwargs):
        return True

    def hit_position(self, dungeon_level, position, source_entity):
        entity = dungeon_level.get_tile(position).get_first_entity()
        if(entity is None):
            return
        damage = random.randrange(0, source_entity._strength)
        damage_types = [entityeffect.DamageTypes.PHYSICAL]
        damage_effect = entityeffect.Damage(source_entity, entity, damage,
                                            damage_types=damage_types)
        entity.add_entity_effect(damage_effect)

    def max_throw_distance(self, source_entity):
        return source_entity._strength + 1
