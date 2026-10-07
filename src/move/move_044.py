from move.base_move import BaseMove


# ひかりのかべ
class LightScreen(BaseMove):
    def __init__(self):
        super().__init__(id=44)
        self.effects = [("set_screen", "light_screen")]
