from move.base_move import BaseMove


# むしくい
class BugBite(BaseMove):
    def __init__(self):
        super().__init__(id=130)
        self.effects = []
