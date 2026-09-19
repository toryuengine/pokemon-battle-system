from move.base_move import BaseMove


# フラッシュ
class Flash(BaseMove):
    def __init__(self):
        super().__init__(id=181)  # 命中率・回避率のランク補正は未対応
        self.effects = []
