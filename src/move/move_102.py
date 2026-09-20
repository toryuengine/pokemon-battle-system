from move.base_move import BaseMove


# ダイビング
class Dive(BaseMove):
    def __init__(self):
        super().__init__(id=102)
        self.effects = []
        self.requires_charge_turn = True
        self.charge_is_invulnerable = True
