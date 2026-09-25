from ability.base_ability import BaseAbility


# きもったま: ノーマル・かくとう技がゴーストタイプに当たる
class Scrappy(BaseAbility):
    ignores_ghost_immunity = True

    def __init__(self):
        super().__init__(id=47)
