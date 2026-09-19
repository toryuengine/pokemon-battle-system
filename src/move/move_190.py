from move.base_move import BaseMove


# あられ
class Hail(BaseMove):
    def __init__(self):
        super().__init__(id=190)  # 天候の変化は未実装
        self.effects = []
