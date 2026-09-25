from ability.shared import UnimplementedAbility


# メロメロボディ: 接触技を受けると30%の確率で相手をメロメロにする（接触判定・メロメロが未実装のため未実装）
class CuteCharm(UnimplementedAbility):
    def __init__(self):
        super().__init__(id=39)
