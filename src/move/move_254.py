from move.base_move import BaseMove


# はどうだん
class AuraSphere(BaseMove):
    def __init__(self):
        super().__init__(id=254)
        self.effects = []
