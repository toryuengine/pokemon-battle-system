from move.base_move import BaseMove


# にほんばれ
class SunnyDay(BaseMove):
    def __init__(self):
        super().__init__(id=21)
        self.effects = [("set_weather", "sun")]
