from move.base_move import BaseMove


# トリック: 自分と相手の持ち物を入れ替える
class Trick(BaseMove):
    def __init__(self):
        super().__init__(id=219)
        self.effects = [("trick",)]
