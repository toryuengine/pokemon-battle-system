from move.base_move import BaseMove


# ドリルくちばし
class DrillPeck(BaseMove):
    def __init__(self):
        super().__init__(id=79)
        self.effects = []
