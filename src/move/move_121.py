from move.base_move import BaseMove


# ほうでん
class Discharge(BaseMove):
    def __init__(self):
        super().__init__(id=121)
        self.effects = [('status', 'target', 'paralysis', 0.3)]
