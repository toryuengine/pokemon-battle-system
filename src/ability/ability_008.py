from ability.shared import UnimplementedAbility


# しめりけ: だいばくはつ・ゆうばくを不発にする（だいばくはつの自爆・ゆうばくが未実装のため未実装）
class Damp(UnimplementedAbility):
    def __init__(self):
        super().__init__(id=8)
