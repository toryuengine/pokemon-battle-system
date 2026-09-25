from ability.shared import UnimplementedAbility


# とうそうしん: 同じ性別の相手への威力1.25倍、異なる性別なら0.75倍（性別のデータが無いため未実装）
class Rivalry(UnimplementedAbility):
    def __init__(self):
        super().__init__(id=54)
