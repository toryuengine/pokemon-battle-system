from move.base_move import BaseMove


# おしおき
class Punishment(BaseMove):
    def __init__(self):
        super().__init__(id=146)
        self.effects = []
