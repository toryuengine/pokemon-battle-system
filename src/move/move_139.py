from move.base_move import BaseMove


# はがねのつばさ
class SteelWing(BaseMove):
    def __init__(self):
        super().__init__(id=139)
        self.effects = [('stat', 'self', 'defense', 1, 0.1)]
