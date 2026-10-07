from move.base_move import BaseMove


# こうごうせい
class Synthesis(BaseMove):
    def __init__(self):
        super().__init__(id=13)
        self.effects = [('heal', 0.5)]
