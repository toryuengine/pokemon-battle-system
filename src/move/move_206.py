from move.base_move import BaseMove


# ゴッドバード
class SkyAttack(BaseMove):
    def __init__(self):
        super().__init__(id=206)  # 溜め技・回避ターンのような複数ターンにまたがる処理は未実装
        self.effects = []
