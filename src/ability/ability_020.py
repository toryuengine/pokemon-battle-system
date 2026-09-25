from ability.base_ability import BaseAbility


# がんじょう: 一撃必殺技を受けない（第4世代ではHP満タンから耐える効果は無い）
class Sturdy(BaseAbility):
    is_breakable = True

    def __init__(self):
        super().__init__(id=20)

    def on_try_hit(self, battle, attacker, defender, move) -> bool:
        return move.is_ohko
