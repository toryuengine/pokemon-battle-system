from move.base_move import BaseMove


# ついばむ
class Peck(BaseMove):
    def __init__(self):
        super().__init__(id=243)
        self.effects = []
