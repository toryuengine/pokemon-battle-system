from move.base_move import BaseMove


# フラッシュ
class Flash(BaseMove):
    def __init__(self):
        super().__init__(id=181)
        self.effects = [("stat", "target", "accuracy", -1, 1.0)]
