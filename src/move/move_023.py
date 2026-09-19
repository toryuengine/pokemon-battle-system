from move.base_move import BaseMove


# かみくだく
class Crunch(BaseMove):
    def __init__(self):
        super().__init__(id=23)
        self.effects = [('stat', 'target', 'defense', -1, 0.2)]
