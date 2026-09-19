from move.base_move import BaseMove


# ステルスロック
class StealthRock(BaseMove):
    def __init__(self):
        super().__init__(id=132)  # 設置技（場に効果を残すタイプ）は未実装
        self.effects = []
