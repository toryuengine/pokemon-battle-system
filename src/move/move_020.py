from move.base_move import BaseMove


# おにび
class WillOWisp(BaseMove):
    def __init__(self):
        super().__init__(id=20)
        self.effects = [('status', 'target', 'burn', 1.0)]
