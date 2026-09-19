from move.base_move import BaseMove


# パワージェム
class PowerGem(BaseMove):
    def __init__(self):
        super().__init__(id=215)
        self.effects = []
