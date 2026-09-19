from move.base_move import BaseMove


# おんねん
class Grudge(BaseMove):
    def __init__(self):
        super().__init__(id=200)  # 交代・拘束・特殊なターン管理などが必要な効果は未実装
        self.effects = []
