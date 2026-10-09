from move.base_move import BaseMove


# しんそく: 第4世代の優先度は+1（+2になったのは第5世代以降）
class ExtremeSpeed(BaseMove):
    def __init__(self):
        super().__init__(id=265)
        self.makes_contact = True
        self.effects = []
        self.priority = 1
