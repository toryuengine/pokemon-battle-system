from move.base_move import BaseMove


# どろかけ
class MudSlap(BaseMove):
    def __init__(self):
        super().__init__(id=241)
        self.effects = [("stat", "target", "accuracy", -1, 1.0)]
