from move.base_move import BaseMove


# うそなき
class FakeTears(BaseMove):
    def __init__(self):
        super().__init__(id=111)
        self.effects = [('stat', 'target', 'spdef', -2, 1.0)]
