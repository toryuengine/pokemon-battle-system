from move.base_move import BaseMove


# がむしゃら
class Flail(BaseMove):
    def __init__(self):
        super().__init__(id=209)
        self.makes_contact = True
        self.effects = []
        self.has_hp_based_power = True
