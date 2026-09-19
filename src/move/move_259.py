from move.base_move import BaseMove


# つつく
class Peck2(BaseMove):
    def __init__(self):
        super().__init__(id=259)
        self.effects = []
