from ability.shared import TypeAbsorbAbility

FLASH_FIRE_MULTIPLIER = 1.5


# もらいび: ほのお技を受けない。受けると、場にいる間自分のほのお技の威力が1.5倍
class FlashFire(TypeAbsorbAbility):
    absorbed_type = "ほのお"

    def __init__(self):
        super().__init__(id=60)
        self.is_active = False

    def on_switch_in(self, battle, pokemon):
        self.is_active = False

    def on_absorb(self, battle, pokemon):
        self.is_active = True

    # 第4世代のもらいびはダメージ計算式で攻撃・特攻と同じ段階に掛かるため、実数値の倍率として扱う
    def get_attack_stat_multiplier(self, attacker, move) -> float:
        if self.is_active and not move.is_typeless and move.type == "ほのお":
            return FLASH_FIRE_MULTIPLIER
        return 1.0
