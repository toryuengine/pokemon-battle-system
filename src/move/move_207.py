from move.base_move import BaseMove


# りゅうせいぐん
class DracoMeteor(BaseMove):
    def __init__(self):
        super().__init__(id=207)
        self.effects = [('stat', 'self', 'spatk', -2, 1.0)]
