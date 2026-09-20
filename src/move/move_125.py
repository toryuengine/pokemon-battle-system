from move.base_move import BaseMove


# あまごい
class RainDance(BaseMove):
    def __init__(self):
        super().__init__(id=125)
        self.effects = [("set_weather", "rain")]
