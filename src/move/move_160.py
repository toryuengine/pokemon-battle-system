from move.base_move import BaseMove


# てんしのキッス
class SweetKiss(BaseMove):
    def __init__(self):
        super().__init__(id=160)
        self.effects = [('status', 'target', 'confusion', 1.0)]
