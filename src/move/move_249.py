from move.base_move import BaseMove


# こうそくいどう
class Agility(BaseMove):
    def __init__(self):
        super().__init__(id=249)
        self.effects = [('stat', 'self', 'spd', 2, 1.0)]
