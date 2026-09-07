import random


def check_hit(hitrate: int) -> bool:
    # move.jsonではhitrate=0が「必中技」を表すため、乱数判定せずに命中とする
    if hitrate == 0:
        return True

    # 1〜100の乱数を引き、hitrate以下なら命中（例: hitrate=75なら75%の確率でTrue）
    return random.randint(1, 100) <= hitrate
