from ability.base_ability import BaseAbility

UNBURDEN_MULTIPLIER = 2.0


# かるわざ: 持ち物を消費すると、場にいる間素早さが2倍
class Unburden(BaseAbility):
    def __init__(self):
        super().__init__(id=57)
        self.is_active = False

    def on_switch_in(self, battle, pokemon):
        self.is_active = False

    def on_item_consumed(self, battle, pokemon):
        self.is_active = True

    def get_speed_multiplier(self, battle, pokemon) -> float:
        return UNBURDEN_MULTIPLIER if self.is_active else 1.0
