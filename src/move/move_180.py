from move.base_move import BaseMove


# たくわえる
class Stockpile(BaseMove):
    def __init__(self):
        super().__init__(id=180)
        self.effects = [('stockpile',)]
