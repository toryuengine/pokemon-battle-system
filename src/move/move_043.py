from move.base_move import BaseMove


# しぼりとる
class WringOut(BaseMove):
    def __init__(self):
        super().__init__(id=43)
        self.effects = []
