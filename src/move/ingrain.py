from move.base_move import BaseMove


# ねをはる
class Ingrain(BaseMove):
    def __init__(self):
        super().__init__(id=5)
        self.heal_ratio = 1 / 16
