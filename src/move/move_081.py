from move.base_move import BaseMove


# ずつき
class Headbutt(BaseMove):
    def __init__(self):
        super().__init__(id=81)
        self.makes_contact = True
        self.effects = [('flinch', 'target', 0.3)]
