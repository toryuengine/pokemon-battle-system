from move.base_move import BaseMove


# トリックルーム
class TrickRoom(BaseMove):
    def __init__(self):
        super().__init__(id=196)
        self.effects = []
