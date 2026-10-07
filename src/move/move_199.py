from move.base_move import BaseMove


# でんげきは
class ZapCannon(BaseMove):
    def __init__(self):
        super().__init__(id=199)
        self.effects = [('status', 'target', 'paralysis', 1.0)]
