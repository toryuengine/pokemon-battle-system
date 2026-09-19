from move.base_move import BaseMove


# かえんほうしゃ
class Flamethrower(BaseMove):
    def __init__(self):
        super().__init__(id=14)
        self.effects = [('status', 'target', 'burn', 0.1)]
