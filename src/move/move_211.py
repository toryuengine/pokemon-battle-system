from move.base_move import BaseMove


# てっぺき
class IronDefense(BaseMove):
    def __init__(self):
        super().__init__(id=211)
        self.effects = [('stat', 'self', 'defense', 2, 1.0)]
