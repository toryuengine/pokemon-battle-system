from move.base_move import BaseMove


# もろはのずつき
class HeadSmash(BaseMove):
    def __init__(self):
        super().__init__(id=232)
        self.makes_contact = True
        self.effects = [('recoil', 0.5)]
