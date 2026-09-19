from move.base_move import BaseMove


# にほんばれ
class SunnyDay(BaseMove):
    def __init__(self):
        super().__init__(id=21)  # 天候の変化は未実装
        self.effects = []
