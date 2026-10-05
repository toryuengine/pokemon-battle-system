from move.base_move import BaseMove


# ドラゴンクロー
class DragonClaw(BaseMove):
    def __init__(self):
        super().__init__(id=125)
        self.makes_contact = True
        self.effects = []
