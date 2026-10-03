from move.base_move import BaseMove


# ふいうち
class Feint(BaseMove):
    def __init__(self):
        super().__init__(id=144)
        self.makes_contact = True
        self.effects = []
        self.priority = 2
