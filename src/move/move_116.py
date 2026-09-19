from move.base_move import BaseMove


# まねっこ
class Mimic(BaseMove):
    def __init__(self):
        super().__init__(id=116)  # 変身・コピー系の特殊な仕様は未実装
        self.effects = []
