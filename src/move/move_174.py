from move.base_move import BaseMove


# あくのはどう
class DarkPulse(BaseMove):
    def __init__(self):
        super().__init__(id=174)
        self.effects = [('flinch', 'target', 0.2)]
