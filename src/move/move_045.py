from move.base_move import BaseMove


# すなあらし
class Sandstorm(BaseMove):
    def __init__(self):
        super().__init__(id=45)
        self.effects = [("set_weather", "sandstorm")]
