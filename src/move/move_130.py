from move.base_move import BaseMove


# にどげり
class DoubleKick(BaseMove):
    def __init__(self):
        super().__init__(id=130)
        self.makes_contact = True
        self.effects = []
        self.min_hits = 2
        self.max_hits = 2
