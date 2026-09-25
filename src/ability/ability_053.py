from ability.shared import UnimplementedAbility


# どくのトゲ: 接触技を受けると30%の確率で相手をどくにする（技の接触判定が未実装のため未実装）
class PoisonPoint(UnimplementedAbility):
    def __init__(self):
        super().__init__(id=53)
