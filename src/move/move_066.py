from move.base_move import BaseMove


# はがねのつばさ
class SteelWing(BaseMove):
    def __init__(self):
        super().__init__(id=66)
        self.makes_contact = True
        self.effects = [('stat', 'self', 'defense', 1, 0.1)]
