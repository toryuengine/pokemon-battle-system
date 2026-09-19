from move.base_move import BaseMove


# スカイアッパー
class SkyUppercut(BaseMove):
    def __init__(self):
        super().__init__(id=126)
        self.effects = []
