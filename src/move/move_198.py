from move.base_move import BaseMove


# メガホーン
class Megahorn(BaseMove):
    def __init__(self):
        super().__init__(id=198)
        self.effects = []
