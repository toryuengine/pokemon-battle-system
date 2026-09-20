from move.base_move import BaseMove


# コメットパンチ
class CometPunch(BaseMove):
    def __init__(self):
        super().__init__(id=266)
        self.effects = []
        self.min_hits = 2
        self.max_hits = 5
