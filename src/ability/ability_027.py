from ability.shared import UnimplementedAbility


# せいでんき: 接触技を受けると30%の確率で相手をまひにする（技の接触判定が未実装のため未実装）
class Static(UnimplementedAbility):
    def __init__(self):
        super().__init__(id=27)
