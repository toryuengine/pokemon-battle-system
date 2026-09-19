from move.base_move import BaseMove


# ダイビング
class Dive(BaseMove):
    def __init__(self):
        super().__init__(id=102)  # 溜め技・回避ターンのような複数ターンにまたがる処理は未実装
        self.effects = []
