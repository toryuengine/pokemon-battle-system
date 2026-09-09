from dataclasses import dataclass


@dataclass
class StatStages:
    atk: int = 0
    defense: int = 0
    spatk: int = 0
    spdef: int = 0
    spd: int = 0


def stage_multiplier(stage: int) -> float:
    if stage < -6 or stage > 6:
        raise ValueError("Stage must be between -6 and 6")
    if stage >= 0:
        return (2 + stage) / 2
    else:
        return 2 / (2 - stage)