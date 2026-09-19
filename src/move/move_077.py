from move.base_move import BaseMove


# かわらわり
class RockSmash(BaseMove):
    def __init__(self):
        super().__init__(id=77)
        self.effects = []
