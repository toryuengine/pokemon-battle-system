from move.base_move import BaseMove


# ものまね
class Transform(BaseMove):
    def __init__(self):
        super().__init__(id=117)  # 変身・コピー系の特殊な仕様は未実装
        self.effects = []
