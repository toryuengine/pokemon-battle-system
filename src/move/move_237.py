from move.base_move import BaseMove


# みやぶる
class Foresight(BaseMove):
    def __init__(self):
        super().__init__(id=237)
        self.effects = [("identify",)]
