from move.base_move import BaseMove


# ばかぢから
class Superpower(BaseMove):
    def __init__(self):
        super().__init__(id=55)
        self.effects = [('stat_multi', 'self', [('atk', -1), ('defense', -1)], 1.0)]
