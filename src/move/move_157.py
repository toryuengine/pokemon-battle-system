from move.base_move import BaseMove


# こうげきしれい
class AttackOrder(BaseMove):
    def __init__(self):
        super().__init__(id=157)
        self.effects = []
