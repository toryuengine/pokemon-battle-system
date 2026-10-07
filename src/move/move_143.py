from move.base_move import BaseMove


# ブレイブバード
class BraveBird(BaseMove):
    def __init__(self):
        super().__init__(id=143)
        self.makes_contact = True
        self.effects = [('recoil', 0.3333333333333333)]
