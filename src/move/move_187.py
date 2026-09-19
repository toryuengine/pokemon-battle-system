from move.base_move import BaseMove


# みずのはどう
class WaterPulse(BaseMove):
    def __init__(self):
        super().__init__(id=187)
        self.effects = [('status', 'target', 'confusion', 0.2)]
