from move.base_move import BaseMove


# ソーラービーム
class SolarBeam(BaseMove):
    def __init__(self):
        super().__init__(id=19)
        self.effects = []
        self.requires_charge_turn = True
