from move.base_move import BaseMove


# おきみやげ
class Memento(BaseMove):
    def __init__(self):
        super().__init__(id=217)
        self.effects = [('stat_multi', 'target', [('atk', -2), ('spatk', -2)], 1.0)]
