from ability.base_ability import BaseAbility


# きょううん: 急所ランク+1
class SuperLuck(BaseAbility):
    crit_stage_bonus = 1

    def __init__(self):
        super().__init__(id=23)
