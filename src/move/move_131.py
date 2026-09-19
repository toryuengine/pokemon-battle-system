from move.base_move import BaseMove


# リベンジ
class Revenge(BaseMove):
    def __init__(self):
        super().__init__(id=131)
        self.effects = []
