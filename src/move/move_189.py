from move.base_move import BaseMove


# こおりのつぶて
class IceShard(BaseMove):
    def __init__(self):
        super().__init__(id=189)
        self.effects = []
