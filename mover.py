import random
from compositecore import Leaf
import direction
import geometry
from position import DungeonLevel
from stats import max_instances_of_composite_on_tile, IntelligenceLevel
from statusflags import StatusFlags


class Mover(Leaf):
    """
    Component for moving and checking if a move is legal.
    """

    def __init__(self):
        super(Mover, self).__init__()
        self.component_type = "mover"

    def can_move(self, new_position, new_dungeon_level=None):
        """
        Checks if parent component can move to new position.
        """
        if new_dungeon_level is None:
            new_dungeon_level = self.parent.dungeon_level.value
        if not new_dungeon_level.get_tile_or_unknown(new_position):
            return False
        try:
            new_tile = new_dungeon_level.get_tile_or_unknown(new_position)
        except IndexError:
            return False
        return (self._can_fit_on_tile(new_tile) and
                self.can_move_to_terrain(new_tile.get_terrain()))

    def move_push_over(self, new_position, dungeon_level=None):
        """
        Will move parent to new position.
        If that position already is occupied try move the old occupant to an adjacent tile.
        The old occupant may be removed if all adjacent tiles are occupied already.

        Returns true if it is successful, false otherwise.
        """
        if dungeon_level is None:
            dungeon_level = self.parent.dungeon_level.value
        if self.try_move(new_position, dungeon_level):
            return True
        old_occupants = self.get_defying_occupants(new_position, dungeon_level)
        for old_occupant in old_occupants:
            old_occupant.mover.try_remove_from_dungeon()

        self.replace_move(new_position, dungeon_level)

        for old_occupant in old_occupants:
            old_occupant.mover.try_move_roll_over(new_position, dungeon_level)
        return True

    def get_defying_occupants(self, position, dungeon_level=None):
        if dungeon_level is None:
            dungeon_level = self.parent.dungeon_level.value
        tile = dungeon_level.get_tile(position)
        return tile.game_pieces[self.parent.game_piece_type.value]

    def try_move_roll_over(self, new_position, new_dungeon_level=None):
        """
        Tries to move parent to new position.
        Or an adjacent tile if it is already occupied.

        Returns true if it is successful, false otherwise.
        """
        if self.try_move(new_position, new_dungeon_level):
            return True
            #  Do not shuffle public constants!
        directions = list(direction.DIRECTIONS)
        random.shuffle(directions)
        for d in directions:
            destination = geometry.add_2d(d, new_position)
            if self.try_move(destination, new_dungeon_level):
                return True
        return False

    def try_move(self, new_position, new_dungeon_level=None):
        """
        Tries to move parent to new position.

        Returns true if it is successful, false otherwise.
        """
        if new_dungeon_level is None:
            new_dungeon_level = self.parent.dungeon_level.value
        if self.can_move(new_position, new_dungeon_level):
            self._move(new_position, new_dungeon_level)
            return True
        return False

    def _move(self, new_position, dungeon_level):
        """
        Moves parent to new position, assumes that it fits there.
        """
        self._remove_from_old_tile()
        dungeon_level.get_tile(new_position).add(self.parent)
        self.parent.position.value = new_position
        if not self.has_sibling("dungeon_level"):
            self.parent.set_child(DungeonLevel())
        self.parent.dungeon_level.value = dungeon_level

    def replace_move(self, new_position, new_dungeon_level=None):
        """
        Moves parent to new position and replaces what was already there.
        """
        if new_dungeon_level is None:
            new_dungeon_level = self.parent.dungeon_level.value
        if not new_dungeon_level.has_tile(new_position):
            return False
        new_tile = new_dungeon_level.get_tile(new_position)
        self._remove_from_old_tile()
        piece_type = self.parent.game_piece_type.value
        new_place = new_tile.game_pieces[piece_type]
        for piece in new_place:
            piece.mover.try_remove_from_dungeon()
        return self.try_move(new_position, new_dungeon_level)

    def _can_fit_on_tile(self, tile):
        """
        Checks if the parent can fit on the tile.
        """
        piece_type = self.parent.game_piece_type
        return len(tile.game_pieces[piece_type.value]) < max_instances_of_composite_on_tile(self.parent)

    def can_move_to_terrain(self, terrain_to_pass):
        if terrain_to_pass is None or terrain_to_pass.has("is_chasm"):
            return True
        elif terrain_to_pass.has("is_solid"):
            return False
        else:
            return self.can_pass_terrain(terrain_to_pass)

    def can_pass_terrain(self, terrain_to_pass):
        """
        Checks if the parent can move through a terrain.
        """
        if terrain_to_pass is None:
            return True
        if self.has_sibling("status_flags"):
            status_flags = self.parent.status_flags
            if terrain_to_pass.has("is_chasm") and status_flags.has_status(StatusFlags.FLYING):
                return True
            if (status_flags.has_status(StatusFlags.CAN_OPEN_DOORS) and
                    terrain_to_pass.has("is_door")):
                return True
        if not terrain_to_pass.has("is_solid") and not terrain_to_pass.has("is_chasm"):
            return True
        return False

    def try_remove_from_dungeon(self):
        """
        Tries to remove parent from dungeon.
        """
        if (not self.has_sibling("dungeon_level") or
                    self.parent.dungeon_level.value is None):
            return True
        if self._remove_from_old_tile():
            self.parent.dungeon_level.value = None
            return True
        return False

    def _remove_from_old_tile(self):
        """
        Removes parent from previous tile.
        """
        if (not self.has_sibling("dungeon_level") or
                    self.parent.dungeon_level.value is None):
            return True
        position = self.parent.position.value
        tile_i_might_be_on = (self.parent.dungeon_level.
                              value.get_tile(position))
        return tile_i_might_be_on.remove(self.parent)


class Stepper(Leaf):
    """
    Component for moving and checking if a move is legal.

    will also interact with what it bumps into.
    """

    def __init__(self):
        super(Stepper, self).__init__()
        self.component_type = "stepper"

    def try_step_in_direction(self, direction):
        return self.try_move_or_bump(geometry.add_2d(self.parent.position.value, direction))

    def try_bump_terrain(self, position):
        terrain_to_step = \
            self.parent.dungeon_level.value.get_tile_or_unknown(position).get_terrain()
        if (terrain_to_step.has("bump_action") and
                terrain_to_step.bump_action.can_bump(self.parent)):
            terrain_to_step.bump_action.bump(self.parent)
            return True
        return False

    def try_attack(self, position):
        return (self.parent.has("attacker") and
                self.parent.attacker.try_hit(position))

    def try_move_or_bump(self, position):
        """
        Tries to move the entity to a position.

        If there is a unfriendly entity in the way hit it instead.
        If there is a door in the way try to open it.
        If an action is taken return True otherwise return False.

        Args:
            position (int, int): The position the entity tries to move to.
        Returns:
            Energy spent
        """
        if self.try_bump_terrain(position):
            return self.parent.movement_speed.value
        if self.try_attack(position):
            return self.parent.melee_speed.value
        if self.parent.mover.try_move(position):
            return self.parent.movement_speed.value
        return 0


def is_tile_dangerous(tile, entity):
    if entity.intelligence.value == IntelligenceLevel.PLANT:
        return False  # Low intelligence ch
    cloud = tile.get_first_cloud()
    if not cloud:
        return False
    damage_effects = [effect for effect in cloud.get_children_with_tag("entity_share_tile_effect")
                      if hasattr(effect, 'damage_types')]

    tolerated_damage_types = [c.damage_type for c in entity.get_children_with_tag("tolerate_damage")]
    for effect in damage_effects:
        for damage_type in effect.damage_types:
            if not damage_type in tolerated_damage_types:
                return True
    return False


class TolerateDamage(Leaf):
    """
    Signifies that that the entity won't mind taking damage of a type.
    """

    def __init__(self, damage_type):
        super(TolerateDamage, self).__init__()
        self.component_type = "tolerate_damage_" + str(damage_type)
        self.tags.add("tolerate_damage")
        self.damage_type = damage_type


class CautiousStepper(Stepper):
    def __init__(self):
        super(CautiousStepper, self).__init__()
        self.component_type = "stepper"

    def dares_to_step(self, position):
        current_position_dangerous =\
            is_tile_dangerous(self.parent.dungeon_level.value.get_tile_or_unknown(self.parent.position.value), self.parent)
        if current_position_dangerous:
            return True  # If the current tile is dangerous any tile is ok. Panic!
        return not is_tile_dangerous(self.parent.dungeon_level.value.get_tile_or_unknown(position), self.parent)

    def try_move_or_bump(self, position):
        """
        Tries to move the entity to a position.

        If there is a door in the way try to open it.
        If there is a unfriendly entity in the way hit it instead.
        **If there is a danger on that tile don't step.**
        If an action is taken return True otherwise return False.

        Args:
            position (int, int): The position the entity tries to move to.
        Returns:
            Energy spent
        """
        if self.try_bump_terrain(position):
            return self.parent.movement_speed.value
        if self.try_attack(position):
            return self.parent.melee_speed.value
        if self.dares_to_step(position):
            move_successful = self.parent.mover.try_move(position)
            return self.parent.movement_speed.value if move_successful else 0
        return 0


class PlayerStepper(Stepper):
    def __init__(self):
        super(PlayerStepper, self).__init__()
        self.component_type = "stepper"

    def try_move_or_bump(self, position):
        """
        Tries to move the entity to a position.

        If there is a door in the way try to open it.
        If there is a unfriendly entity in the way hit it instead.
        **If there is a danger on that tile don't step.**
        If an action is taken return True otherwise return False.

        Args:
            position (int, int): The position the entity tries to move to.
        Returns:
            Energy spent
        """
        if self.try_bump_terrain(position):
            return self.parent.movement_speed.value
        if self.try_attack(position):
            return self.parent.melee_speed.value
        terrain = self.parent.dungeon_level.value.get_tile_or_unknown(position).get_terrain()
        if ((len(terrain.get_children_with_tag("prompt_player")) < 1) or
                terrain.get_children_with_tag("prompt_player")[0].prompt_player(target_entity=self.parent)):
            if self.parent.mover.try_move(position):
                return self.parent.movement_speed.value
        return 0


class ImmobileStepper(Stepper):
    def __init__(self):
        super(ImmobileStepper, self).__init__()
        self.component_type = "stepper"

    def try_move_or_bump(self, position):
        return self.parent.movement_speed.value


class RandomStepper(Stepper):
    def __init__(self):
        super(RandomStepper, self).__init__()
        self.component_type = "stepper"

    def try_move_or_bump(self, _):
        new_position = geometry.add_2d(random.choice(direction.DIRECTIONS), self.parent.position.value)
        return super(RandomStepper, self).try_move_or_bump(new_position)


class SlimeCanShareTileEntityMover(Mover):
    """
    Parent entities with this mover may enter tiles of other entities.
    """

    def __init__(self):
        super(SlimeCanShareTileEntityMover, self).__init__()

    def _can_fit_on_tile(self, tile):
        """
        Slime monsters fight by entering the tile of another entity.
        Therefore it must override '_can_fit_on_tile' so it doesn't think
        A tile with an entity is too crowded.
        """
        piece_type = self.parent.game_piece_type.value
        entities_on_tile = tile.game_pieces[piece_type]
        if (len(entities_on_tile) == 0 or
                (len(entities_on_tile) == 1 and not entities_on_tile[0].has("is_slime"))):
            return True
        return False


def teleport_monsters(player):
    positions = (player.dungeon_level.value.get_walkable_positions(player, player.position.value))
    random_positions = random.sample(positions, len(positions))
    max_tries = 30
    while len(player.vision.get_seen_entities()) > 0 and max_tries > 0:
        entity = player.vision.get_seen_entities()[0]
        for position in random_positions:
            teleport_successful = entity.mover.try_move(position)
            if teleport_successful:
                break
        max_tries -= 1