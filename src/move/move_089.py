from move.base_move import BaseMove


# ギガインパクト
class GigaImpact(BaseMove):
    def __init__(self):
        super().__init__(id=89)  # 反動で次ターン行動不能になる仕様は未実装
        self.effects = []
