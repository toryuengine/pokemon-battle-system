from move.base_move import BaseMove


# こおりのつぶて: 優先度+1の先制技。接触しない
class IceShard(BaseMove):
    def __init__(self):
        super().__init__(id=189)
        self.effects = []
        self.priority = 1
