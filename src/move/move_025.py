from move.base_move import BaseMove


# ブラストバーン
class BlastBurn(BaseMove):
    def __init__(self):
        super().__init__(id=25)
        self.effects = []
        self.requires_recharge = True
