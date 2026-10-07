from move.base_move import BaseMove


# いばる
class Swagger(BaseMove):
    def __init__(self):
        super().__init__(id=136)
        self.effects = [('stat', 'target', 'atk', 2, 1.0), ('status', 'target', 'confusion', 1.0)]
