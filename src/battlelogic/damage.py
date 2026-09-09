import random

from battlelogic.type_chart import get_effectiveness, resolve_type_id
from move.base_move import CATEGORY_PHYSICAL, CATEGORY_STATUS

# jsonの実数値にレベルが織り込まれておらず、データ上レベルを特定できないため
# 便宜上レベル100固定で計算する（両者同条件なので相対的なダメージ比較には影響しない）
LEVEL = 100


def calculate_damage(attacker, defender, move) -> int:
    # 変化技(CATEGORY_STATUS)はダメージを与えない
    if move.category == CATEGORY_STATUS:
        return 0

    # 物理技(CATEGORY_PHYSICAL)はatk/defense、それ以外(特殊)はspatk/spdefを使う
    if move.category == CATEGORY_PHYSICAL:
        attack_stat = attacker.status.atk
        defense_stat = defender.status.defense
    else:
        attack_stat = attacker.status.spatk
        defense_stat = defender.status.spdef

    base_damage = (2 * LEVEL / 5 + 2) * move.power * attack_stat / defense_stat
    base_damage = base_damage / 50 + 2

    is_stab = resolve_type_id(move.type) in (attacker.type1, attacker.type2)
    stab = 1.5 if is_stab else 1.0

    effectiveness = get_effectiveness(move.type, defender.type1, defender.type2)
    random_factor = random.randint(85, 100) / 100

    damage = base_damage * stab * effectiveness * random_factor
    return int(damage)
