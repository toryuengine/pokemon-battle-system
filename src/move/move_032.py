from move.base_move import BaseMove


# たきのぼり
class Waterfall(BaseMove):
    def __init__(self):
        super().__init__(id=32)
        self.makes_contact = True
        self.effects = [('flinch', 'target', 0.2)]
