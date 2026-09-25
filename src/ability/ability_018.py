from ability.shared import UnimplementedAbility


# ほうし: 接触技を受けると30%の確率で相手をどく・まひ・ねむりにする（技の接触判定が未実装のため未実装）
class EffectSpore(UnimplementedAbility):
    def __init__(self):
        super().__init__(id=18)
