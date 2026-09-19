from move.base_move import BaseMove


# すなかけ
class SandAttack(BaseMove):
    def __init__(self):
        super().__init__(id=250)  # 命中率・回避率のランク補正は未対応
        self.effects = []
