from move.base_move import BaseMove


# くさむすび
class GrassKnot(BaseMove):
    def __init__(self):
        super().__init__(id=33)
        self.effects = []
