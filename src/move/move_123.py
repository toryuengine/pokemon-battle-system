from move.base_move import BaseMove


# メロメロ
class Attract(BaseMove):
    def __init__(self):
        super().__init__(id=123)
        self.effects = []
