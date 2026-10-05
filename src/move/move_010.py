from move.base_move import BaseMove


# こごえるかぜ
class IcyWind(BaseMove):
    def __init__(self):
        super().__init__(id=10)
        self.effects = [('stat', 'target', 'spd', -1, 1.0)]
