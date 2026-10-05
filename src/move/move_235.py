from move.base_move import BaseMove


# すなかけ
class SandAttack(BaseMove):
    def __init__(self):
        super().__init__(id=235)
        self.effects = [("stat", "target", "accuracy", -1, 1.0)]
