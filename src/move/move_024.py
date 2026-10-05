from move.base_move import BaseMove


# かみくだく
class Crunch(BaseMove):
    def __init__(self):
        super().__init__(id=24)
        self.makes_contact = True
        self.effects = [('stat', 'target', 'defense', -1, 0.2)]
