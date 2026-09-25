from ability.shared import UnimplementedAbility


# ほのおのからだ: 接触技を受けると30%の確率で相手をやけどにする（技の接触判定が未実装のため未実装）
class FlameBody(UnimplementedAbility):
    def __init__(self):
        super().__init__(id=86)
