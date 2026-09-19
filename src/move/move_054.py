from move.base_move import BaseMove


# いわなだれ
class RockSlide(BaseMove):
    def __init__(self):
        super().__init__(id=54)
        self.effects = [('flinch', 'target', 0.3)]
