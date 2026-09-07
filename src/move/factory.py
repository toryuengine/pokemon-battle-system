from move.amnesia import Amnesia
from move.base_move import BaseMove
from move.crunch import Crunch
from move.curse import Curse
from move.dragon_claw import DragonClaw
from move.earthquake import Earthquake
from move.flare_drive import FlareDrive
from move.frenzy_plant import FrenzyPlant
from move.giga_drain import GigaDrain
from move.hyper_beam import HyperBeam
from move.ingrain import Ingrain
from move.leaf_storm import LeafStorm
from move.leech_seed import LeechSeed
from move.outrage import Outrage
from move.seed_bomb import SeedBomb
from move.sleep_powder import SleepPowder
from move.sludge_bomb import SludgeBomb
from move.synthesis import Synthesis

_MOVE_CLASSES = {
    0: LeafStorm,
    1: SludgeBomb,
    2: Amnesia,
    3: SleepPowder,
    4: GigaDrain,
    5: Ingrain,
    6: LeechSeed,
    7: SeedBomb,
    8: Earthquake,
    9: Outrage,
    10: Curse,
    11: FrenzyPlant,
    12: HyperBeam,
    13: Synthesis,
    22: FlareDrive,
    23: Crunch,
    24: DragonClaw,
}


def create_move(move_id: int) -> BaseMove:
    move_class = _MOVE_CLASSES.get(move_id)
    if move_class is None:
        return BaseMove(move_id)
    return move_class()
