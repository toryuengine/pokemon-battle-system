from move.base_move import BaseMove


# かげうち
class ShadowSneak(BaseMove):
    def __init__(self):
        super().__init__(id=223)
        self.effects = []
        self.priority = 1
