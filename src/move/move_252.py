from move.base_move import BaseMove

# 使った後の残りPPごとの威力（残りPP4以上は40）
TRUMP_CARD_POWER_BY_PP = {0: 200, 1: 80, 2: 60, 3: 50}
TRUMP_CARD_BASE_POWER = 40


# きりふだ: 使った後の残りPPが少ないほど威力が高くなる（4以上→40、3→50、2→60、1→80、0→200）。
# PPは技を出した時点で消費済みなので、current_ppがそのまま「使った後の残りPP」になる（プレッシャーで2減った分も反映される）
class TrumpCard(BaseMove):
    def __init__(self):
        super().__init__(id=252)
        self.effects = []

    def get_power(self, battle, attacker, defender) -> int:
        return TRUMP_CARD_POWER_BY_PP.get(self.current_pp, TRUMP_CARD_BASE_POWER)
