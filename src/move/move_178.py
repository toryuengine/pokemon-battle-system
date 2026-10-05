from move.base_move import BaseMove


# ミラーショット
class MirrorShot(BaseMove):
    def __init__(self):
        super().__init__(id=178)
        self.effects = [("stat", "target", "accuracy", -1, 0.3)]
