from move.base_move import BaseMove


# ねこだまし
class FakeOut(BaseMove):
    def __init__(self):
        super().__init__(id=74)
        self.effects = [('flinch', 'target', 1.0)]
