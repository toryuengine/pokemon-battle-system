from move.base_move import BaseMove


# まねっこ
class Mimic(BaseMove):
    def __init__(self):
        super().__init__(id=116)
        self.effects = [("mimic",)]
