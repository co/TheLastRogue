from compositecore import Composite
from mover import Mover
from statusflags import StatusFlags
from text import Description

dummy_flyer = Composite()
dummy_flyer.set_child(StatusFlags([StatusFlags.FLYING]))
dummy_flyer.set_child(Mover())
dummy_flyer.set_child(Description("flyer_dummy", "Just a dummy used for instead a flyer for calculations."))

dummy_player = Composite()
dummy_player.set_child(StatusFlags([StatusFlags.CAN_OPEN_DOORS]))
dummy_player.set_child(Mover())
dummy_player.set_child(Description("player_dummy", "Just a dummy used for instead of player for calculations."))
