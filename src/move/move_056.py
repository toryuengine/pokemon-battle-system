from move.base_move import BaseMove


# ものまね
class Transform(BaseMove):
    def __init__(self):
        super().__init__(id=56)
        self.effects = [("transform",)]
