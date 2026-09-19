from move.base_move import BaseMove


# シザークロス
class XScissor(BaseMove):
    def __init__(self):
        super().__init__(id=59)
        self.effects = []
