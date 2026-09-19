from move.base_move import BaseMove


# つきのひかり
class Moonlight(BaseMove):
    def __init__(self):
        super().__init__(id=253)
        self.effects = [('heal', 0.5)]
