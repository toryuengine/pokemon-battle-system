from ability.base_ability import BaseAbility


# かたやぶり: 相手の特性（受ける側で働くもの）を無視して技を出す
class MoldBreaker(BaseAbility):
    ignores_target_ability = True

    def __init__(self):
        super().__init__(id=62)
