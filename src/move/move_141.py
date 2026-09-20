from move.base_move import BaseMove


# そらをとぶ
class Fly(BaseMove):
    def __init__(self):
        super().__init__(id=141)
        self.effects = []
        self.requires_charge_turn = True
        self.charge_is_invulnerable = True
