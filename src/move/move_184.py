from move.base_move import BaseMove


# だましうち
class SuckerPunch(BaseMove):
    def __init__(self):
        super().__init__(id=184)
        self.effects = []
        self.priority = 1
