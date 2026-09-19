from move.base_move import BaseMove


# のろい
class Curse(BaseMove):
    def __init__(self):
        super().__init__(id=10)
        self.effects = [('stat_multi', 'self', [('atk', 1), ('defense', 1), ('spd', -1)], 1.0)]
