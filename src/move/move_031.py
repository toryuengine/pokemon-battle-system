from move.base_move import BaseMove


# ミラーコート
class MirrorCoat(BaseMove):
    def __init__(self):
        super().__init__(id=31)
        self.effects = []
