from move.base_move import BaseMove


# メタルバースト
class MetalBurst(BaseMove):
    def __init__(self):
        super().__init__(id=214)
        self.effects = []
