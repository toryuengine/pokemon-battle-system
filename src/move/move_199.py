from move.base_move import BaseMove


# でんげきは: 必ず命中する（hitrate=0）。追加効果は無い
class ShockWave(BaseMove):
    def __init__(self):
        super().__init__(id=199)
        self.effects = []
