from move.base_move import BaseMove


# どくどくのキバ
class PoisonFang(BaseMove):
    def __init__(self):
        super().__init__(id=209)
        self.effects = [('status', 'target', 'poison', 0.3)]
