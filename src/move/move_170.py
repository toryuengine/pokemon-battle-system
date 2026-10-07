from move.base_move import BaseMove


# かみつく
class Bite(BaseMove):
    def __init__(self):
        super().__init__(id=170)
        self.makes_contact = True
        self.effects = [('flinch', 'target', 0.3)]
