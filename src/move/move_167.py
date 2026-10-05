from move.base_move import BaseMove


# リフレクター
class Reflect(BaseMove):
    def __init__(self):
        super().__init__(id=167)
        self.effects = [("set_screen", "reflect")]
