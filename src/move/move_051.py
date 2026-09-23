from move.base_move import BaseMove


# こらえる
class Endure(BaseMove):
    def __init__(self):
        super().__init__(id=51)
        self.effects = [("endure",)]
        self.priority = 4
