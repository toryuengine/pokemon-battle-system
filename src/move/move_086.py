from move.base_move import BaseMove


# トライアタック
class TriAttack(BaseMove):
    def __init__(self):
        super().__init__(id=86)
        self.effects = [('status_random', 'target', ['burn', 'freeze', 'paralysis'], 0.2)]
