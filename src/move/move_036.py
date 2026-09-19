from move.base_move import BaseMove


# アクアテール
class AquaTail(BaseMove):
    def __init__(self):
        super().__init__(id=36)
        self.effects = []
