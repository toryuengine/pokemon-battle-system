from move.base_move import BaseMove


# まもる
class Protect(BaseMove):
    def __init__(self):
        super().__init__(id=65)
        self.effects = [("protect",)]
        self.priority = 3
