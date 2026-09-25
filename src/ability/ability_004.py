from ability.base_ability import BaseAbility


# ありじごく: 地面にいる相手（ひこうタイプ・ふゆう・でんじふゆう中でない相手）を交代できなくする
class ArenaTrap(BaseAbility):
    def __init__(self):
        super().__init__(id=4)

    def traps_opponent(self, battle, opponent) -> bool:
        return battle.is_grounded(opponent)
