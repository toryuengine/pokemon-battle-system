from move.base_move import BaseMove


# ダブルアタック
class DoubleHit(BaseMove):
    def __init__(self):
        super().__init__(id=194)  # 複数回攻撃は未実装
        self.effects = []
