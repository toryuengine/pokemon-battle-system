from move.base_move import BaseMove


# じんつうりき
class Extrasensory(BaseMove):
    def __init__(self):
        super().__init__(id=186)
        self.effects = [('flinch', 'target', 0.1)]
