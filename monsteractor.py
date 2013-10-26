import random
import geometry as geo
import rng
import direction
import terrain
from actor import Actor
import libtcodpy as libtcod
from statusflags import StatusFlags


class ChasePlayerActor(Actor):
    """
    Standard Monster AI will chase the player.
    """
    def __init__(self):
        super(ChasePlayerActor, self).__init__()


class StepRandomDirectonActor(Actor):
    """
    Standard Monster AI will chase the player.
    """
    def __init__(self):
        super(ChasePlayerActor, self).__init__()

class MonsterActor(Actor):
    """
    Standard Monster AI will chase the player.
    """
    def __init__(self):
        super(MonsterActor, self).__init__()

    def try_step_random_direction(self):
        """
        Tries to make the entity step to a random direction.
        If the step succeeds True is return otherwise False.
        """
        random_direction = random.sample(list(direction.DIRECTIONS), 1)[0]
        new_position = geo.add_2d(self.position, random_direction)
        return self.try_move_to(new_position)

    def try_open_door(self, door):
        """
        Will try to open the door.
        If the entity can't open doors or
        the door is already open return False.

        Args:
            door (Door): The door terrain that should be opened)
        """
        if(self.has_status(StatusFlags.CAN_OPEN_DOORS) and not door.is_open):
            door.open()
            return True
        return False

    def get_entity_sharing_my_position(self):
        """
        Sometimes two entities can share a tile this method
        returns the other entity if this is currently the case.
        If the number of entities of this tile is neither 1 or 2
        raise an exception as this is an invalid state.
        """
        entities_on_my_tile =\
            self.dungeon_level.get_tile(self.position).get_entities()
        if(len(entities_on_my_tile) == 1):
            return None
        if(len(entities_on_my_tile) != 2):
            raise
        return next(entity for entity in entities_on_my_tile
                    if not entity is self)

    def try_to_escape_slime(self):
        """
        Assumes the entity is trapped by a slime,
        if escape is successful return true otherwise false.
        """
        slime = self.get_entity_sharing_my_position()
        if not slime is None:
            self.hit(slime)
        escape_successful = rng.coin_flip() and rng.coin_flip()
        return escape_successful

    def get_seen_entities(self):
        """
        Gets all entities seen by this entity not including self.
        """
        seen_entities = []
        for entity in self.dungeon_level.entities:
            if self.can_see_point(entity.position):
                seen_entities.append(entity)
        return [entity for entity in seen_entities if not entity is self]

    def get_seen_entities_closest_first(self):
        """
        Gets all seen entities sorted on distance from self not including self.
        """
        return sorted(self.get_seen_entities(),
                      key=lambda entity: geo.chess_distance(self.position,
                                                            entity.position))

    def get_closest_seen_entity(self):
        """
        Gets the closest of all seen entities not including self.
        """
        closest_seen_entities = self.get_seen_entities_closest_first()
        if(len(closest_seen_entities) < 1):
            return None
        return closest_seen_entities[0]

    def can_see_point(self, point):
        """
        Checks if a particular point is visible to this entity.

        Args:
            point (int, int): The point to check.
        """
        x, y = point
        return libtcod.map_is_in_fov(self.dungeon_map, x, y)
