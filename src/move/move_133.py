from move.base_move import BaseMove


# ストーンエッジ
class StoneEdge(BaseMove):
    def __init__(self):
        super().__init__(id=133)
        self.effects = []
        self.high_crit = True
