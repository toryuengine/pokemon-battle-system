from move.base_move import BaseMove


# ボルテッカー
class VoltTackle(BaseMove):
    def __init__(self):
        super().__init__(id=257)
        self.makes_contact = True
        self.effects = [('recoil', 0.3333333333333333)]
