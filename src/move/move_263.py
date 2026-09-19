from move.base_move import BaseMove


# テクスチャー2
class UnknownMove263(BaseMove):
    def __init__(self):
        super().__init__(id=263)  # 独自技のため詳細不明。追加効果は未対応扱い
        self.effects = []
