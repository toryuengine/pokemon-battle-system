from move.base_move import BaseMove


# にほんばれ
class SunnyDay(BaseMove):
    def __init__(self):
        super().__init__(id=15)
        self.effects = [("set_weather", "sun")]
