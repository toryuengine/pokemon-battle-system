from move.base_move import BaseMove
from move.crunch import Crunch
from move.dragon_claw import DragonClaw
from move.earthquake import Earthquake
from move.flare_drive import FlareDrive

_MOVE_CLASSES = {
    8: Earthquake,
    22: FlareDrive,
    23: Crunch,
    24: DragonClaw,
}


def create_move(move_id: int) -> BaseMove:
    move_class = _MOVE_CLASSES.get(move_id)
    if move_class is None:
        return BaseMove(move_id)
    return move_class()
