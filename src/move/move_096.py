from move.base_move import BaseMove


# みきり
class Detect(BaseMove):
    def __init__(self):
        super().__init__(id=96)  # 回避・耐久系の特殊な仕様は未実装
        self.effects = []
        self.priority = 3
