from move.base_move import CATEGORY_SPECIAL, BaseMove


# ミラーコート: 優先度-5。このターンに本体が特殊技で最後に受けたダメージの2倍を相手に与える。
# 特殊技でダメージを受けていなければ失敗する。あくタイプには当たらない（エスパー技のため）
class MirrorCoat(BaseMove):
    def __init__(self):
        super().__init__(id=31)
        self.effects = []
        self.priority = -5
        self.has_fixed_damage = True

    def try_execute(self, battle, attacker, defender) -> bool:
        return attacker.current_status.last_damage_category_this_turn == CATEGORY_SPECIAL

    def get_fixed_damage(self, battle, attacker, defender) -> int:
        return attacker.current_status.last_damage_taken_this_turn * 2
