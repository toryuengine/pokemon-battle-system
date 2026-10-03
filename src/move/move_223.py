from move.base_move import BaseMove


# かげうち
class ShadowSneak(BaseMove):
    def __init__(self):
        super().__init__(id=223)
        self.makes_contact = True
        self.effects = []
        self.priority = 1
