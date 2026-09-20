from move.base_move import BaseMove


# ギガインパクト
class GigaImpact(BaseMove):
    def __init__(self):
        super().__init__(id=89)
        self.effects = []
        self.requires_recharge = True
