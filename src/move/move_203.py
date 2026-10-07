from move.base_move import BaseMove


# ミルクのみ
class MilkDrink(BaseMove):
    def __init__(self):
        super().__init__(id=203)
        self.effects = [('heal', 0.5)]
