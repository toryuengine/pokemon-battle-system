from move.base_move import BaseMove


# きあいだま
class FocusBlast(BaseMove):
    def __init__(self):
        super().__init__(id=180)
        self.effects = [('stat', 'target', 'spdef', -1, 0.1)]
