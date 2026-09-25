from ability.shared import UnimplementedAbility


# ゆうばく: 接触技で瀕死にされると相手に最大HPの1/4のダメージ（技の接触判定が未実装のため未実装）
class Aftermath(UnimplementedAbility):
    def __init__(self):
        super().__init__(id=32)
