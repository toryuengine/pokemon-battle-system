from ability.shared import UnimplementedAbility


# ありじごく: 相手を交代できなくする（プレイヤー判断による交代が無いため未実装）
class ArenaTrap(UnimplementedAbility):
    def __init__(self):
        super().__init__(id=4)
