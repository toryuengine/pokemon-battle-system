from move.base_move import BaseMove


# はかいこうせん
class HyperBeam(BaseMove):
    def __init__(self):
        super().__init__(id=12)
        self.requires_recharge = True
