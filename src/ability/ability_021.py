from ability.base_ability import BaseAbility


# するどいめ: 相手に命中率を下げられない
class KeenEye(BaseAbility):
    is_breakable = True

    def __init__(self):
        super().__init__(id=21)

    def prevents_stat_drop(self, stat_name) -> bool:
        return stat_name == "accuracy"
