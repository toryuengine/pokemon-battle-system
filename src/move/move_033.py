from move.base_move import BaseMove


# きあいパンチ
class FocusPunch(BaseMove):
    def __init__(self):
        super().__init__(id=33)  # 優先度（先制技）は未対応
        self.effects = []
