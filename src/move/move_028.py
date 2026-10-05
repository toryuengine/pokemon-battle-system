from move.base_move import BaseMove


# つばめがえし
class AerialAce(BaseMove):
    def __init__(self):
        super().__init__(id=28)
        self.makes_contact = True
        self.effects = []
