from move.base_move import BaseMove


# ハイドロカノン
class HydroCannon(BaseMove):
    def __init__(self):
        super().__init__(id=39)
        self.effects = []
        self.requires_recharge = True
