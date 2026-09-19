from move.base_move import BaseMove


# アクアジェット
class AquaJet(BaseMove):
    def __init__(self):
        super().__init__(id=80)  # 優先度（先制技）は未対応
        self.effects = []
