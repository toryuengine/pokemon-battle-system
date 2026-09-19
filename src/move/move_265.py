from move.base_move import BaseMove


# しんそく
class ExtremeSpeed(BaseMove):
    def __init__(self):
        super().__init__(id=265)  # 優先度（先制技）は未対応
        self.effects = []
