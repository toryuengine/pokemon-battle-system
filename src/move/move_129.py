from move.base_move import BaseMove


# ジャイロボール
class GyroBall(BaseMove):
    def __init__(self):
        super().__init__(id=129)
        self.effects = []
