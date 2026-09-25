from ability.base_ability import BaseAbility

POISON_HEAL_RATIO = 1 / 8


# ポイズンヒール: どく状態の間、ターン終了時にダメージを受ける代わりに最大HPの1/8回復する
class PoisonHeal(BaseAbility):
    def __init__(self):
        super().__init__(id=19)

    def on_residual_status(self, battle, pokemon, condition) -> bool:
        if condition != "poison":
            return False
        battle.apply_heal(pokemon, POISON_HEAL_RATIO)
        return True
