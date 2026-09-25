from move.base_move import BaseMove


# いちゃもん: 相手が同じ技を2回続けて出せなくする
class Torment(BaseMove):
    def __init__(self):
        super().__init__(id=188)
        self.effects = [("torment",)]
