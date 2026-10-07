from move.base_move import BaseMove


# はねやすめ
class Roost(BaseMove):
    def __init__(self):
        super().__init__(id=142)
        self.effects = [('heal', 0.5)]
