from move.base_move import BaseMove


# あくび
class Yawn(BaseMove):
    def __init__(self):
        super().__init__(id=103)
        self.effects = []
