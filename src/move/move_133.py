from move.base_move import BaseMove


# どくびし
class ToxicSpikes(BaseMove):
    def __init__(self):
        super().__init__(id=133)
        self.effects = [("set_hazard", "toxic_spikes")]
