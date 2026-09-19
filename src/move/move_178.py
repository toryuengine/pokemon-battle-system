from move.base_move import BaseMove


# はきだす
class SpitUp(BaseMove):
    def __init__(self):
        super().__init__(id=178)  # 交代・拘束・特殊なターン管理などが必要な効果は未実装
        self.effects = []
