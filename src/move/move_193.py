from move.base_move import BaseMove


# じこあんじ: 相手の能力ランク（命中率・回避率を含む）を、そのまま自分にコピーする
class PsychUp(BaseMove):
    def __init__(self):
        super().__init__(id=193)
        self.effects = [("psych_up",)]
