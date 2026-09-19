from move.base_move import BaseMove


# とっておき
class LastResort(BaseMove):
    def __init__(self):
        super().__init__(id=195)
        self.effects = []
