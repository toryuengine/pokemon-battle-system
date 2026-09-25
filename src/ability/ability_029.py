from ability.shared import UnimplementedAbility


# ねんちゃく: 持ち物を奪われない（トリック・はたきおとす等が未実装のため未実装）
class StickyHold(UnimplementedAbility):
    def __init__(self):
        super().__init__(id=29)
