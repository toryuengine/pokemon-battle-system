from move.base_move import BaseMove


# でんじは
class ThunderWave(BaseMove):
    def __init__(self):
        super().__init__(id=105)
        self.effects = [('status', 'target', 'paralysis', 1.0)]
