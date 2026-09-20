from move.base_move import BaseMove


# でんこうせっか
class QuickAttack(BaseMove):
    def __init__(self):
        super().__init__(id=49)
        self.effects = []
        self.priority = 1
