from move.base_move import BaseMove


# めいそう
class CalmMind(BaseMove):
    def __init__(self):
        super().__init__(id=100)
        self.effects = [('stat_multi', 'self', [('spatk', 1), ('spdef', 1)], 1.0)]
