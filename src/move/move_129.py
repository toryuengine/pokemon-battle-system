from move.base_move import BaseMove

GYRO_BALL_MAX_POWER = 150


# ジャイロボール: 相手より自分が遅いほど威力が高くなる。威力 = 25 × 相手の素早さ ÷ 自分の素早さ + 1（最大150）。
# 素早さはランク補正・まひ・持ち物・特性を反映した、実際に行動順の判定に使う値で比べる
class GyroBall(BaseMove):
    def __init__(self):
        super().__init__(id=129)
        self.effects = []

    def get_power(self, battle, attacker, defender) -> int:
        attacker_speed = battle.get_effective_speed(attacker)
        if attacker_speed <= 0:
            return 1
        return min(GYRO_BALL_MAX_POWER, 25 * battle.get_effective_speed(defender) // attacker_speed + 1)
