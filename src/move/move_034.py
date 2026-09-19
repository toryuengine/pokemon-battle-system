from move.base_move import BaseMove


# かげぶんしん
class DoubleTeam(BaseMove):
    def __init__(self):
        super().__init__(id=34)  # 命中率・回避率のランク補正は未対応
        self.effects = []
