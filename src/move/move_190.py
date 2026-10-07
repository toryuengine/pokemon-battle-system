from move.base_move import BaseMove


# あられ
class Hail(BaseMove):
    def __init__(self):
        super().__init__(id=190)
        self.effects = [("set_weather", "hail")]
