from dataclasses import dataclass


@dataclass
class StatStages:
    atk: int = 0
    defense: int = 0
    spatk: int = 0
    spdef: int = 0
    spd: int = 0
    # 命中率・回避率のランク（えんまく・かげぶんしん等）。他の能力値と同じ-6〜+6だが、
    # 倍率の計算式は異なる（accuracy_stage_multiplierを使う）
    accuracy: int = 0
    evasion: int = 0


def stage_multiplier(stage: int) -> float:
    if stage < -6 or stage > 6:
        raise ValueError("Stage must be between -6 and 6")
    if stage >= 0:
        return (2 + stage) / 2
    else:
        return 2 / (2 - stage)


# 命中率・回避率専用の段階倍率。atk等とは基準が2ではなく3になる（本編仕様）
def accuracy_stage_multiplier(stage: int) -> float:
    if stage < -6 or stage > 6:
        raise ValueError("Stage must be between -6 and 6")
    if stage >= 0:
        return (3 + stage) / 3
    else:
        return 3 / (3 - stage)