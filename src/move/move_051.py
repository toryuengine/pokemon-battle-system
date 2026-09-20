from move.base_move import BaseMove


# こらえる
class Endure(BaseMove):
    def __init__(self):
        super().__init__(id=51)  # 回避・耐久系の特殊な仕様は未実装
        self.effects = []
        self.priority = 4
