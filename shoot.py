import statestack
import geometry as geo
import positionexaminer


def player_select_missile_path(source_entity, max_throw_distance,
                               game_state):
    """
    Method initiating a prompt for the player to select a missile path.
    """
    choose_target_prompt = statestack.StateStack()
    target_entity = source_entity.vision.get_closest_seen_entity()
    if(not target_entity is None and
       geo.chess_distance(target_entity.position.value,
                          source_entity.position.value) <= max_throw_distance):
        init_target = target_entity.position.value
    else:
        init_target = source_entity.position.value
    destination_selector = positionexaminer.\
        MissileDestinationSelector(choose_target_prompt,
                                   source_entity.position.value,
                                   source_entity,
                                   game_state,
                                   max_throw_distance,
                                   init_target=init_target)
    choose_target_prompt.push(destination_selector)
    choose_target_prompt.main_loop()
    return destination_selector.selected_path


class MissileHitDetection(object):
    """
    Is able to detect collisions on a given path.
    """
    def __init__(self, passes_entity=False, passes_solid=False):
        self.passes_entity = passes_entity
        self.passes_solid = passes_solid

    def get_path_taken(self, path, dungeon_level):
        """
        Returns a list of points of the path until the collision occured.
        """
        for index, point in enumerate(path):
            tile = dungeon_level.get_tile_or_unknown(point)
            if tile.get_terrain().has("is_solid") and not self.passes_solid:
                return self._last_n_or_default(path, index, None)
            if tile.has_entity() and not self.passes_entity:
                return self._last_n_or_default(path, index + 1, None)
        return self._last_n_or_default(path, index + 1, None)

    def _last_n_or_default(self, the_list, n, default):
        """
        Help function for getting last n elements of a list or default value.
        """
        if n > len(the_list):
            return default
        else:
            return the_list[:n]
