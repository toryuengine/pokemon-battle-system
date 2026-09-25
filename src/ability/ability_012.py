from ability.shared import UnimplementedAbility


# どんかん: メロメロ状態にならない（メロメロが未実装のため未実装）
class Oblivious(UnimplementedAbility):
    def __init__(self):
        super().__init__(id=12)
