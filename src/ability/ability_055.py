from ability.shared import UnimplementedAbility


# きゅうばん: ほえる・ふきとばしで交代させられない（強制交代の技が未実装のため未実装）
class SuctionCups(UnimplementedAbility):
    def __init__(self):
        super().__init__(id=55)
