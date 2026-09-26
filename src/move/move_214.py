from move.base_move import BaseMove


# メタルバースト: このターンに本体が攻撃技（物理・特殊どちらでも）で最後に受けたダメージの1.5倍を相手に与える。
# 優先度は0なので、相手より先に行動するとダメージを受けておらず失敗する
class MetalBurst(BaseMove):
    def __init__(self):
        super().__init__(id=214)
        self.effects = []
        self.has_fixed_damage = True

    def try_execute(self, battle, attacker, defender) -> bool:
        return attacker.current_status.last_damage_category_this_turn is not None

    def get_fixed_damage(self, battle, attacker, defender) -> int:
        return int(attacker.current_status.last_damage_taken_this_turn * 1.5)
