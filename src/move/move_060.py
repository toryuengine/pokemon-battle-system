from move.base_move import BaseMove


# つじぎり
class NightSlash(BaseMove):
    def __init__(self):
        super().__init__(id=60)
        self.makes_contact = True
        self.effects = []
        self.high_crit = True
