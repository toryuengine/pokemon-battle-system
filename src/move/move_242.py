from move.base_move import BaseMove


# ウェザーボール
class WeatherBall(BaseMove):
    def __init__(self):
        super().__init__(id=242)
        self.effects = []
