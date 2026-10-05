from move.base_move import BaseMove


# スピードスター
class Swift(BaseMove):
    def __init__(self):
        super().__init__(id=91)
        self.effects = []
