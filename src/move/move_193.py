from move.base_move import BaseMove


# じこあんじ
class PsychUp(BaseMove):
    def __init__(self):
        super().__init__(id=193)  # 変身・コピー系の特殊な仕様は未実装
        self.effects = []
