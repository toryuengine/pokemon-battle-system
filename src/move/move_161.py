from move.base_move import BaseMove


# わるだくみ
class NastyPlot(BaseMove):
    def __init__(self):
        super().__init__(id=161)
        self.effects = [('stat', 'self', 'spatk', 2, 1.0)]
