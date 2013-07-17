import statestack
import geometry as geo
import positionexaminer


def player_select_missile_path(source_entity, max_throw_distance,
                               game_gamestate):
    choose_target_prompt = statestack.StateStack()
    target_entity = source_entity.get_closest_seen_entity()
    if(not target_entity is None and
       geo.chess_distance(target_entity.position, source_entity.position)
       <= max_throw_distance):
        init_target = target_entity.position
    else:
        init_target = source_entity.position
    destination_selector = positionexaminer.\
        MissileDestinationSelector(choose_target_prompt,
                                   source_entity.position.copy(),
                                   source_entity,
                                   game_gamestate,
                                   max_throw_distance,
                                   init_target=init_target)
    choose_target_prompt.push(destination_selector)
    choose_target_prompt.main_loop()
    return destination_selector.selected_path


class MissileHitDetection(object):
    def __init__(self, passes_entity=False, passes_solid=False):
        self.passes_entity = passes_entity
        self.passes_solid = passes_solid

    def get_path_taken(self, path, dungeon_level):
        for index, point in enumerate(path):
            tile = dungeon_level.get_tile_or_unknown(point)
            if(tile.get_terrain().is_solid() and not self.passes_solid):
                return path[:index - 1]
            if(tile.has_entity() and not self.passes_entity):
                return path[:index + 1]
        return path[:index]
