from move.base_move import BaseMove


# はかいこうせん
class HyperBeam(BaseMove):
    def __init__(self):
        super().__init__(id=184)
        self.effects = []
        self.requires_recharge = True
