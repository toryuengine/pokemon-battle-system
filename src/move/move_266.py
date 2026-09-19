from move.base_move import BaseMove


# コメットパンチ
class CometPunch(BaseMove):
    def __init__(self):
        super().__init__(id=266)  # 複数回攻撃は未実装
        self.effects = []
