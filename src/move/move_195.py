from move.base_move import BaseMove


# アクアジェット
class AquaJet(BaseMove):
    def __init__(self):
        super().__init__(id=195)
        self.makes_contact = True
        self.effects = []
        self.priority = 1
