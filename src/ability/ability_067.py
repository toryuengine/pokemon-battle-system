from ability.base_ability import BaseAbility


# ノーガード: 自分が出す技・自分が受ける技が必ず命中する（あなをほる等で隠れている相手にも当たる）
class NoGuard(BaseAbility):
    always_hits = True

    def __init__(self):
        super().__init__(id=67)
