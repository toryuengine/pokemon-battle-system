from move.base_move import BaseMove


# タマゴうみ
class UnknownMove264(BaseMove):
    def __init__(self):
        super().__init__(id=264)  # 独自技のため詳細不明。追加効果は未対応扱い
        self.effects = []
