from ability.base_ability import BaseAbility

HEATPROOF_MULTIPLIER = 0.5
# 通常のやけどダメージ（最大HPの1/16）の半分
HEATPROOF_BURN_DAMAGE_RATIO = 1 / 32


# たいねつ: 受けるほのお技の威力が半分。やけどのダメージが半分
class Heatproof(BaseAbility):
    is_breakable = True

    def __init__(self):
        super().__init__(id=65)

    def get_received_power_multiplier(self, defender, move) -> float:
        if not move.is_typeless and move.type == "ほのお":
            return HEATPROOF_MULTIPLIER
        return 1.0

    def on_residual_status(self, battle, pokemon, condition) -> bool:
        if condition != "burn":
            return False
        battle.apply_damage(pokemon, max(1, int(pokemon.status.hp * HEATPROOF_BURN_DAMAGE_RATIO)))
        return True
