from move.base_move import BaseMove


# なまける
class SlackOff(BaseMove):
    def __init__(self):
        super().__init__(id=255)
        self.effects = [('heal', 0.5)]
