from move.base_move import BaseMove


# アンコール: 相手が直前に使った技を、4〜8ターンの間出し続けさせる
class Encore(BaseMove):
    def __init__(self):
        super().__init__(id=164)
        self.effects = [("encore",)]
