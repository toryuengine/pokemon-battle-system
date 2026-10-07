from move.base_move import BaseMove


# かなしばり: 相手が直前に使った技を、4〜7ターンの間使えなくする
class Disable(BaseMove):
    def __init__(self):
        super().__init__(id=165)
        self.effects = [("disable",)]
