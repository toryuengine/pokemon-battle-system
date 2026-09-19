from move.base_move import BaseMove


# しおみず
class Brine(BaseMove):
    def __init__(self):
        super().__init__(id=202)
        self.effects = []
