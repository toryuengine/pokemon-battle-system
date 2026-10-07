from move.base_move import BaseMove


# あやしいひかり
class ConfuseRay(BaseMove):
    def __init__(self):
        super().__init__(id=122)
        self.effects = [('status', 'target', 'confusion', 1.0)]
