from move.base_move import BaseMove


# クロスポイズン
class CrossPoison(BaseMove):
    def __init__(self):
        super().__init__(id=177)
        self.makes_contact = True
        self.effects = [('status', 'target', 'poison', 0.1)]
        self.high_crit = True
