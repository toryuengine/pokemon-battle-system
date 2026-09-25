from ability.base_ability import BaseAbility
from move.base_move import CATEGORY_STATUS


# ふゆう: じめん技を受けない。まきびし・どくびしも受けない（くろいてっきゅうを持っている、またはねをはるで根を張っていると無効）
class Levitate(BaseAbility):
    is_breakable = True
    is_levitating = True

    def __init__(self):
        super().__init__(id=46)

    def on_try_hit(self, battle, attacker, defender, move) -> bool:
        if move.is_typeless or move.type != "じめん" or move.category == CATEGORY_STATUS:
            return False
        return not defender.is_forced_grounded
