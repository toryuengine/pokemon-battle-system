from move.base_move import BaseMove


# すてみタックル
class TakeDown(BaseMove):
    def __init__(self):
        super().__init__(id=138)
        self.effects = []
