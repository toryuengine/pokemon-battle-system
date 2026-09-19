from move.base_move import BaseMove


# どろかけ
class MudSlap(BaseMove):
    def __init__(self):
        super().__init__(id=241)  # 命中率・回避率のランク補正は未対応
        self.effects = []
