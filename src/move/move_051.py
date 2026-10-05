from move.base_move import BaseMove


# サイコキネシス
class Psychic(BaseMove):
    def __init__(self):
        super().__init__(id=51)
        self.effects = [('stat', 'target', 'spdef', -1, 0.1)]
