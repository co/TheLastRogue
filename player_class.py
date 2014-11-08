from health import Health
from player import new_player
from stats import Class, DataTypes, DataPoint


def new_knight_player(game_state):
    player = new_player(game_state)
    player.set_child(Health(25))
    player.set_child(DataPoint(DataTypes.CLASS, Class.KNIGHT))
    return player


def new_rogue_player(game_state):
    player = new_player(game_state)
    player.set_child(Health(20))
    player.set_child(DataPoint(DataTypes.CLASS, Class.ROGUE))
    return player


def new_gunslinger_player(game_state):
    player = new_player(game_state)
    player.set_child(Health(18))
    player.set_child(DataPoint(DataTypes.CLASS, Class.GUNSLINGER))
    return player


def new_tinker_player(game_state):
    player = new_player(game_state)
    player.set_child(Health(15))
    player.set_child(DataPoint(DataTypes.CLASS, Class.GUNSLINGER))
    return player

CLASS_FACTORIES = [new_knight_player, new_rogue_player, new_gunslinger_player, new_tinker_player]


def get_new_player_set(game_state):
    return map(lambda f: f(game_state), CLASS_FACTORIES)
