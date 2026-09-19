from move.base_move import BaseMove


# だましうち
class SuckerPunch(BaseMove):
    def __init__(self):
        super().__init__(id=184)  # 優先度（先制技）は未対応
        self.effects = []
