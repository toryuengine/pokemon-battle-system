from ability.base_ability import BaseAbility


# かいりきバサミ: 相手に攻撃を下げられない
class HyperCutter(BaseAbility):
    is_breakable = True

    def __init__(self):
        super().__init__(id=61)

    def prevents_stat_drop(self, stat_name) -> bool:
        return stat_name == "atk"
