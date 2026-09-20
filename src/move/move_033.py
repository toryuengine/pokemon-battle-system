from move.base_move import BaseMove


# きあいパンチ
class FocusPunch(BaseMove):
    def __init__(self):
        super().__init__(id=33)
        self.effects = []
        self.priority = -3
