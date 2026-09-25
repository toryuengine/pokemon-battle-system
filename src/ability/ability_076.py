from ability.base_ability import BaseAbility


# リーフガード: にほんばれの間、状態異常にならない（こんらんは防げない）
class LeafGuard(BaseAbility):
    is_breakable = True

    def __init__(self):
        super().__init__(id=76)

    def can_receive_status(self, battle, pokemon, condition) -> bool:
        return condition == "confusion" or battle.get_effective_weather() != "sun"
