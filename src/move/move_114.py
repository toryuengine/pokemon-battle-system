from move.base_move import BaseMove


# くろいまなざし: 相手を逃げられなくする
class MeanLook(BaseMove):
    def __init__(self):
        super().__init__(id=114)
        self.effects = [("mean_look",)]
