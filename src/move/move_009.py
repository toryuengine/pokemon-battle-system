from move.base_move import BaseMove


# げきりん
class Outrage(BaseMove):
    def __init__(self):
        super().__init__(id=9)
        self.effects = []
