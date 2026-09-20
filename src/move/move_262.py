from move.base_move import BaseMove


# がんせきほう
class RockWrecker(BaseMove):
    def __init__(self):
        super().__init__(id=262)
        self.effects = []
        self.requires_recharge = True
