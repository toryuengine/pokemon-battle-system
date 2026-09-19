from move.base_move import BaseMove


# いちゃもん
class Torment(BaseMove):
    def __init__(self):
        super().__init__(id=188)  # 交代・拘束・特殊なターン管理などが必要な効果は未実装
        self.effects = []
