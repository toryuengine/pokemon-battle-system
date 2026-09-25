from ability.base_ability import BaseAbility


# いしあたま: 反動ダメージを受けない（わるあがきの反動は受ける）
class RockHead(BaseAbility):
    prevents_recoil = True

    def __init__(self):
        super().__init__(id=5)
