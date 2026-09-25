from ability.base_ability import BaseAbility

QUICK_FEET_MULTIPLIER = 1.5


# はやあし: 状態異常の間、素早さが1.5倍。まひによる素早さの低下を受けない
class QuickFeet(BaseAbility):
    ignores_paralysis_speed_drop = True

    def __init__(self):
        super().__init__(id=11)

    def get_speed_multiplier(self, battle, pokemon) -> float:
        if pokemon.current_status.status_condition is not None:
            return QUICK_FEET_MULTIPLIER
        return 1.0
