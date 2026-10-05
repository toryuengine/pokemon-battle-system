from move.base_move import BaseMove


# あやしいひかり
class ConfuseRay(BaseMove):
    def __init__(self):
        super().__init__(id=105)
        self.effects = [('status', 'target', 'confusion', 1.0)]
