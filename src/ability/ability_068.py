from ability.base_ability import BaseAbility


# くいしんぼう: チイラ・ヤタピ・カムラのみをHP1/2以下で食べる
class Gluttony(BaseAbility):
    pinch_berry_hp_ratio = 1 / 2

    def __init__(self):
        super().__init__(id=68)
