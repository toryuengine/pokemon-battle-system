from ability.base_ability import BaseAbility


# クリアボディ: 相手に能力ランクを下げられない
class ClearBody(BaseAbility):
    is_breakable = True

    def __init__(self):
        super().__init__(id=69)

    def prevents_stat_drop(self, stat_name) -> bool:
        return True
