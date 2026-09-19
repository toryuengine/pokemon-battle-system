from move.base_move import BaseMove


# カウンター
class Counter(BaseMove):
    def __init__(self):
        super().__init__(id=69)
        self.effects = []
