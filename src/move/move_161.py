from move.base_move import BaseMove


# チャージビーム
class ChargeBeam(BaseMove):
    def __init__(self):
        super().__init__(id=161)
        self.effects = [('stat', 'self', 'spatk', 1, 0.7)]
