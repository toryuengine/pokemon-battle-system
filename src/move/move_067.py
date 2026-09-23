from move.base_move import BaseMove


# だくりゅう
class MuddyWater(BaseMove):
    def __init__(self):
        super().__init__(id=67)
        self.effects = [("stat", "target", "accuracy", -1, 0.3)]
