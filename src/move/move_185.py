from move.base_move import BaseMove


# ハイパーボイス
class HyperVoice(BaseMove):
    def __init__(self):
        super().__init__(id=185)
        self.effects = []
