from move.base_move import BaseMove


# ゴッドバード
class SkyAttack(BaseMove):
    def __init__(self):
        super().__init__(id=206)
        self.effects = []
        self.requires_charge_turn = True
