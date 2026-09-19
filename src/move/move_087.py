from move.base_move import BaseMove


# すなあらし
class Sandstorm(BaseMove):
    def __init__(self):
        super().__init__(id=87)  # 天候の変化は未実装
        self.effects = []
