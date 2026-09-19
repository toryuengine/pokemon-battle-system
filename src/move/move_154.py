from move.base_move import BaseMove


# かいふくしれい
class HealOrder(BaseMove):
    def __init__(self):
        super().__init__(id=154)
        self.effects = [('heal', 0.5)]
