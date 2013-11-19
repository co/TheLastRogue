import random
import colors
from compositecore import Leaf
import geometry as geo
from graphic import GraphicChar
from health import DamageTakenEffect
import rng
import direction
from messenger import messenger
from statusflags import StatusFlags
from actor import Actor


class MonsterActorState(Leaf):
    """
    Holds the monster actor state of the parent. This value is used in AI decisions.
    """
    WANDERING = 0
    HUNTING = 1

    def __init__(self, state=WANDERING):
        super(MonsterActorState, self).__init__()
        self.component_type = "monster_actor_state"
        self._value = state

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if (self._value != MonsterActorState.HUNTING and
                    MonsterActorState.HUNTING == new_value):
            found_gfx = GraphicChar(None, colors.BLUE, "!")
            (self.parent.char_printer.
             append_graphic_char_temporary_frames([found_gfx]))
            messenger.message(self.parent.entity_messages.notice)

        self._value = new_value


class MonsterActor(Actor):
    """
    A set of methods useful to compose an AI Actor.
    """

    def __init__(self):
        super(MonsterActor, self).__init__()

    def try_step_random_direction(self):
        """
        Tries to make the entity step to a random direction.
        If the step succeeds True is return otherwise False.
        """
        random_direction = random.sample(list(direction.DIRECTIONS), 1)[0]
        new_position = geo.add_2d(self.parent.position.value, random_direction)
        return self.parent.mover.try_move_or_bump(new_position)

    def get_entity_sharing_my_position(self):
        """
        Sometimes two entities can share a tile this method
        returns the other entity if this is currently the case.
        If the number of entities of this tile is neither 1 or 2
        raise an exception as this is an invalid state.
        """
        dungeon_level = self.parent.dungeon_level.value
        position = self.parent.position.value
        entities_on_my_tile = (dungeon_level.get_tile(position).get_entities())
        if len(entities_on_my_tile) == 1:
            return None
        if len(entities_on_my_tile) != 2:
            raise
        return next(entity for entity in entities_on_my_tile
                    if not entity is self)

    def can_see_player(self):
        seen_entities = self.parent.vision.get_seen_entities()
        return any(entity.has_child("is_player")
                   for entity in seen_entities)

    def get_player_if_seen(self):
        seen_entities = self.parent.vision.get_seen_entities()
        found_player = next((entity for entity in seen_entities
                             if (entity.has_child("is_player"))), None)
        if (not found_player is None and
                not found_player.status_flags.has_status(StatusFlags.INVISIBILE)):
            return found_player
        return None

    def set_path_to_player_if_seen(self):
        player = self.get_player_if_seen()
        if player is None:
            return False
        if self.parent.monster_actor_state.value == MonsterActorState.HUNTING:
            self.parent.path.compute_path(player.position.value)
            return True
        return False

    def notice_player_check(self):
        player = self.get_player_if_seen()
        if player is None:
            return False
        return self.parent.awareness_checker.check(player.stealth.value)

    def set_path_to_random_walkable_point(self):
        positions = self.get_walkable_positions_from_my_position()
        destination = random.sample(positions, 1)[0]
        self.parent.path.compute_path(destination)

    def get_walkable_positions_from_my_position(self):
        dungeon_level = self.parent.dungeon_level.value
        position = self.parent.position.value
        return dungeon_level.get_walkable_positions(self.parent, position)

    def do_range_attack(self):
        """
        Does the ranged attack, assumes that can_do_ranged_attack returned True.
        """
        player = self.get_player_if_seen()
        if player is None:
            return False
        return self.parent.monster_range_attack_action.act(player.position.value)

    def can_do_ranged_attack(self):
        """
        Returns true if it's possible for the monster to do a ranged attack at the player.
        """
        player = self.get_player_if_seen()
        if player is None or MonsterActorState.HUNTING != self.parent.monster_actor_state.value:
            return False
        if (not self.parent.has_child("monster_range_attack_action") or
                not self.parent.monster_range_attack_action.can_act(player.position.value)):
            return False
        range_attack = self.parent.monster_range_attack_action
        return (range_attack.is_destination_within_range(player.position.value) and
                not range_attack.is_something_blocking(player.position.value))


class StepRandomDirectionActor(MonsterActor):
    """
    Standard Monster AI will chase the player.
    """

    def __init__(self):
        super(StepRandomDirectionActor, self).__init__()

    def act(self):
        self.try_step_random_direction()
        return self.parent.movement_speed.value


class ChasePlayerActor(MonsterActor):
    """
    Standard Monster AI will chase the player.
    """

    def __init__(self):
        super(ChasePlayerActor, self).__init__()

    def act(self):
        self.parent.dungeon_mask.update_fov()

        #  Perform Stealth Check
        if self.notice_player_check():
            self.parent.monster_actor_state.value = MonsterActorState.HUNTING

        #  Set Path
        self.set_path_to_player_if_seen()
        if not self.parent.path.has_path():
            self.set_path_to_random_walkable_point()

        #  Do action
        if self.can_do_ranged_attack():
            self.do_range_attack()
        else:
            self.parent.path.try_step_path()

        return self.parent.movement_speed.value


class HuntPlayerIfHurtMe(DamageTakenEffect):
    def __init__(self):
        super(HuntPlayerIfHurtMe, self).__init__()
        self.component_type = "hunt_player_if_hurt_me"

    def effect(self, _, source_entity):
        if source_entity.has_child("is_player"):
            self.parent.monster_actor_state.value = MonsterActorState.HUNTING

#    def try_to_escape_slime(self):
#        """
#        Assumes the entity is trapped by a slime,
#        if escape is successful return true otherwise false.
#        """
#        slime = self.get_entity_sharing_my_position()
#        if not slime is None:
#            self.parent.attacker.hit(slime)
#        escape_successful = rng.coin_flip() and rng.coin_flip()
#        return escape_successful
