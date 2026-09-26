from move.base_move import CATEGORY_PHYSICAL, BaseMove


# カウンター: 優先度-5。このターンに本体が物理技で最後に受けたダメージの2倍を相手に与える。
# 物理技でダメージを受けていなければ失敗する。ゴーストタイプには当たらない（かくとう技のため）
class Counter(BaseMove):
    def __init__(self):
        super().__init__(id=69)
        self.effects = []
        self.priority = -5
        self.has_fixed_damage = True

    def try_execute(self, battle, attacker, defender) -> bool:
        return attacker.current_status.last_damage_category_this_turn == CATEGORY_PHYSICAL

    def get_fixed_damage(self, battle, attacker, defender) -> int:
        return attacker.current_status.last_damage_taken_this_turn * 2
