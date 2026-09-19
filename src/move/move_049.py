from move.base_move import BaseMove


# でんこうせっか
class QuickAttack(BaseMove):
    def __init__(self):
        super().__init__(id=49)  # 優先度（先制技）は未対応
        self.effects = []
