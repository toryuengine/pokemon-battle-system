from move.base_move import BaseMove


# りゅうのまい
class DragonDance(BaseMove):
    def __init__(self):
        super().__init__(id=56)
        self.effects = [('stat_multi', 'self', [('atk', 1), ('spd', 1)], 1.0)]
