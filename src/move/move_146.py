from dataclasses import astuple

from move.base_move import BaseMove

PUNISHMENT_MAX_POWER = 200


# おしおき: 相手の能力ランクが上がっているほど威力が高くなる。
# 威力 = 60 + 20 × 相手の上がっているランクの合計（命中率・回避率も含む。下がっているランクは数えない。最大200）
class Punishment(BaseMove):
    def __init__(self):
        super().__init__(id=146)
        self.effects = []

    def get_power(self, battle, attacker, defender) -> int:
        positive_stages = sum(stage for stage in astuple(battle.get_stages(defender)) if stage > 0)
        return min(PUNISHMENT_MAX_POWER, 60 + 20 * positive_stages)
