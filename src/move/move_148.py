from move.base_move import BaseMove


# つっぱり
class ArmThrust(BaseMove):
    def __init__(self):
        super().__init__(id=148)
        self.effects = []
        self.min_hits = 2
        self.max_hits = 5
