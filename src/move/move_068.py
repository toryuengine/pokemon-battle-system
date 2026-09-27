from move.base_move import BaseMove


# だいちのちから
class EarthPower(BaseMove):
    def __init__(self):
        super().__init__(id=68)
        self.effects = [('stat', 'target', 'spdef', -1, 0.1)]
