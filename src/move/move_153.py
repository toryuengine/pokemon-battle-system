from move.base_move import BaseMove


# クロスチョップ
class CrossChop(BaseMove):
    def __init__(self):
        super().__init__(id=153)
        self.makes_contact = True
        self.effects = []
        self.high_crit = True
