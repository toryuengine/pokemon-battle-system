from move.base_move import BaseMove


# ソーラービーム
class SolarBeam(BaseMove):
    def __init__(self):
        super().__init__(id=19)  # 溜め技・回避ターンのような複数ターンにまたがる処理は未実装
        self.effects = []
