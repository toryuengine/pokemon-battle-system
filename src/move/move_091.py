from move.base_move import BaseMove


# ボーンラッシュ
class BoneRush(BaseMove):
    def __init__(self):
        super().__init__(id=91)  # 複数回攻撃は未実装
        self.effects = []
