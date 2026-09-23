from move.base_move import BaseMove


# テクスチャー2
class Conversion2(BaseMove):
    def __init__(self):
        super().__init__(id=263)
        self.effects = [("type_change_resist",)]
