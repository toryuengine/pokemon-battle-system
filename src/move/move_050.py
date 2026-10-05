from move.base_move import BaseMove


# でんじは: じめんタイプには効果が無い
class ThunderWave(BaseMove):
    def __init__(self):
        super().__init__(id=50)
        self.checks_type_immunity = True
        self.effects = [('status', 'target', 'paralysis', 1.0)]
