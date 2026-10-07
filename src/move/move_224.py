from move.base_move import BaseMove


# ちいさくなる（第4世代仕様のため回避率+1。第6世代以降は+2）
class Minimize(BaseMove):
    def __init__(self):
        super().__init__(id=224)
        self.effects = [("stat", "self", "evasion", 1, 1.0)]
