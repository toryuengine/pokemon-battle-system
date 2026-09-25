from move.base_move import BaseMove

SPIT_UP_POWER_PER_STOCKPILE = 100


# はきだす: たくわえた回数×100の威力で攻撃し、たくわえた効果（回数と、防御・特防の上昇）を解除する
# たくわえていなければ失敗する
class SpitUp(BaseMove):
    def __init__(self):
        super().__init__(id=178)
        self.effects = [("release_stockpile",)]

    def try_execute(self, battle, attacker, defender) -> bool:
        return attacker.current_status.stockpile_count > 0

    def get_power(self, attacker) -> int:
        return SPIT_UP_POWER_PER_STOCKPILE * attacker.current_status.stockpile_count
