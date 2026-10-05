from move.base_move import BaseMove


# シグナルビーム
class SignalBeam(BaseMove):
    def __init__(self):
        super().__init__(id=9)
        self.effects = [('status', 'target', 'confusion', 0.1)]
