import statestack
import positionexaminer


def player_select_missile_path(entity, max_throw_distance, game_gamestate):
    choose_target_prompt = statestack.StateStack()
    init_target = entity.get_closest_seen_entity().position
    if init_target is None:
        init_target = entity.position
    destination_selector = positionexaminer.\
        MissileDestinationSelector(choose_target_prompt,
                                   entity.position.copy(),
                                   entity,
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
