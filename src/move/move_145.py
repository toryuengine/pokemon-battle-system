from move.base_move import BaseMove


# どろばくだん
class MudBomb(BaseMove):
    def __init__(self):
        super().__init__(id=145)
        self.effects = [("stat", "target", "accuracy", -1, 0.3)]
