from move.base_move import BaseMove


# ついばむ: 相手がきのみを持っていれば、奪って食べてその効果を自分が得る
class Peck(BaseMove):
    def __init__(self):
        super().__init__(id=243)
        self.effects = [("eat_berry",)]
