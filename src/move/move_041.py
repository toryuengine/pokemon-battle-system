from move.base_move import BaseMove


# どくどく: 相手をもうどく状態にする
class Toxic(BaseMove):
    def __init__(self):
        super().__init__(id=41)
        self.effects = [('status', 'target', 'toxic', 1.0)]
