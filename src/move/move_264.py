from move.base_move import BaseMove


# タマゴうみ
class EggLay(BaseMove):
    def __init__(self):
        super().__init__(id=264)
        self.effects = [("heal", 0.5)]
