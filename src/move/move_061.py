from move.base_move import BaseMove


# りゅうのはどう
class DragonPulse(BaseMove):
    def __init__(self):
        super().__init__(id=61)
        self.effects = []
