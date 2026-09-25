from ability.shared import UnimplementedAbility


# じりょく: はがねタイプの相手を交代できなくする（プレイヤー判断による交代が無いため未実装）
class MagnetPull(UnimplementedAbility):
    def __init__(self):
        super().__init__(id=78)
