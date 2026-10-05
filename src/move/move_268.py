from move.base_move import BaseMove


# ラスターパージ: 50%で相手の特防-1
class LusterPurge(BaseMove):
    def __init__(self):
        super().__init__(id=268)
        self.effects = [('stat', 'target', 'spdef', -1, 0.5)]
