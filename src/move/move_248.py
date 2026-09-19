from move.base_move import BaseMove


# むしのさざめき
class BugBuzz(BaseMove):
    def __init__(self):
        super().__init__(id=248)
        self.effects = []
