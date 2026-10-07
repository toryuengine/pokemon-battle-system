from move.base_move import BaseMove


# まきびし
class Spikes(BaseMove):
    def __init__(self):
        super().__init__(id=134)
        self.effects = [("set_hazard", "spikes")]
