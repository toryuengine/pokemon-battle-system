from move.base_move import BaseMove


# みがわり
class Substitute(BaseMove):
    def __init__(self):
        super().__init__(id=42)  # 変身・コピー系の特殊な仕様は未実装
        self.effects = []
