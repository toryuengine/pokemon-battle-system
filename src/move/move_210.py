from move.base_move import BaseMove


# にどげり
class DoubleKick(BaseMove):
    def __init__(self):
        super().__init__(id=210)
        self.effects = []
        self.min_hits = 2
        self.max_hits = 2
