from ability.shared import UnimplementedAbility


# ぶきよう: 持ち物の効果が無くなる（未実装）
class Klutz(UnimplementedAbility):
    def __init__(self):
        super().__init__(id=40)
