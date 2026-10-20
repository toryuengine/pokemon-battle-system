import random


# rngは乱数（random.Randomのインスタンス等）。省略するとrandomモジュールを使う
def check_hit(hitrate: int, rng=random) -> bool:
    # move.jsonではhitrate=0が「必中技」を表すため、乱数判定せずに命中とする
    if hitrate == 0:
        return True

    # 1〜100の乱数を引き、hitrate以下なら命中（例: hitrate=75なら75%の確率でTrue）
    return rng.randint(1, 100) <= hitrate
