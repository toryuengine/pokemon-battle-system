from move.base_move import BaseMove


# しびれごな
class StunSpore(BaseMove):
    def __init__(self):
        super().__init__(id=240)
        self.effects = [('status', 'target', 'paralysis', 1.0)]
