from move.base_move import BaseMove


# シャドークロー
class ShadowClaw(BaseMove):
    def __init__(self):
        super().__init__(id=48)
        self.makes_contact = True
        self.effects = []
        self.high_crit = True
