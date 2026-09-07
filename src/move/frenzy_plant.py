from move.base_move import BaseMove


# ハードプラント
class FrenzyPlant(BaseMove):
    def __init__(self):
        super().__init__(id=11)
        self.requires_recharge = True
