from move.base_move import BaseMove


# ステルスロック
class StealthRock(BaseMove):
    def __init__(self):
        super().__init__(id=132)
        self.effects = [("set_hazard", "stealth_rock")]
