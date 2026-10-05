from move.base_move import BaseMove


# あなをほる
class Dig(BaseMove):
    def __init__(self):
        super().__init__(id=234)
        self.makes_contact = True
        self.effects = []
        self.requires_charge_turn = True
        self.charge_is_invulnerable = True
