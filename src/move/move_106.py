from move.base_move import BaseMove

FACADE_BOOSTED_CONDITIONS = ("poison", "paralysis", "burn")


# からげんき: 自分がどく・まひ・やけどのとき威力が2倍になる
# (第4世代仕様で、やけどによる物理技のダメージ半減は受ける。ただしやけどの半減自体が未実装)
class Facade(BaseMove):
    def __init__(self):
        super().__init__(id=106)
        self.effects = []

    def get_power(self, battle, attacker, defender) -> int:
        if attacker.current_status.status_condition in FACADE_BOOSTED_CONDITIONS:
            return self.power * 2
        return self.power
