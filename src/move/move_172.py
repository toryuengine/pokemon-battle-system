from move.base_move import BaseMove


# がむしゃら: 相手の残りHPを自分の残りHPと同じにする（差の分だけダメージを与える）。
# 自分の残りHPが相手以上なら失敗する。ゴーストタイプには当たらない（タイプ相性の無効だけを見る固定ダメージ技）
class Endeavor(BaseMove):
    def __init__(self):
        super().__init__(id=172)
        self.makes_contact = True
        self.effects = []
        self.has_fixed_damage = True

    def try_execute(self, battle, attacker, defender) -> bool:
        return attacker.current_status.current_hp < defender.current_status.current_hp

    def get_fixed_damage(self, battle, attacker, defender) -> int:
        return max(0, defender.current_status.current_hp - attacker.current_status.current_hp)
