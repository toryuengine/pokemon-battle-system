from move.base_move import BaseMove


# ダブルアタック
class DoubleHit(BaseMove):
    def __init__(self):
        super().__init__(id=194)
        self.effects = []
        self.min_hits = 2
        self.max_hits = 2
