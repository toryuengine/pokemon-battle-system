from move.base_move import BaseMove


# えんまく
class Smokescreen(BaseMove):
    def __init__(self):
        super().__init__(id=16)
        self.effects = [("stat", "target", "accuracy", -1, 1.0)]
