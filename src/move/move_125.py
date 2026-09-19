from move.base_move import BaseMove


# あまごい
class RainDance(BaseMove):
    def __init__(self):
        super().__init__(id=125)  # 天候の変化は未実装
        self.effects = []
