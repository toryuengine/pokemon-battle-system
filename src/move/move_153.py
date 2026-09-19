from move.base_move import BaseMove


# あやしいかぜ
class OminousWind(BaseMove):
    def __init__(self):
        super().__init__(id=153)
        self.effects = [('stat_multi', 'self', [('atk', 1), ('defense', 1), ('spatk', 1), ('spdef', 1), ('spd', 1)], 0.1)]
