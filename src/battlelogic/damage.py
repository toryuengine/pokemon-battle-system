import random

from battlelogic.type_chart import get_move_effectiveness, resolve_type_id
from move.base_move import CATEGORY_PHYSICAL, CATEGORY_STATUS

# jsonの実数値にレベルが織り込まれておらず、データ上レベルを特定できないため
# 便宜上レベル100固定で計算する（両者同条件なので相対的なダメージ比較には影響しない）
LEVEL = 100

# 急所の発生率。通常は1/16、急所に当たりやすい技(high_crit)は1/8
NORMAL_CRIT_CHANCE = 1 / 16
HIGH_CRIT_CHANCE = 1 / 8
# 第4世代の急所ダメージ倍率（第6世代以降の1.5倍とは異なる）
CRIT_MULTIPLIER = 2.0

TYPE_ID_ROCK = 12

# ソーラービームのid。晴れ以外での溜め省略・雨での威力半減という固有仕様があるため個別に参照する
SOLAR_BEAM_ID = 19


# 天候によるほのお/みず技の威力補正。ソーラービームは雨で別途さらに半減する
def get_weather_power_multiplier(move, weather) -> float:
    multiplier = 1.0

    if weather == "sun":
        if move.type == "ほのお":
            multiplier *= 1.5
        elif move.type == "みず":
            multiplier *= 0.5
    elif weather == "rain":
        if move.type == "みず":
            multiplier *= 1.5
        elif move.type == "ほのお":
            multiplier *= 0.5
        if move.id == SOLAR_BEAM_ID:
            multiplier *= 0.5

    return multiplier


def calculate_damage(attacker, defender, move, weather=None, screen_active=False) -> int:
    # 変化技(CATEGORY_STATUS)はダメージを与えない
    if move.category == CATEGORY_STATUS:
        return 0

    # 一撃必殺技: タイプ相性が0倍(無効)なら失敗、それ以外は相手の残りHPと同じ量のダメージで即座に瀕死にする
    if move.is_ohko:
        if get_move_effectiveness(move, defender) == 0:
            return 0
        return defender.current_status.current_hp

    # 物理技(CATEGORY_PHYSICAL)はatk/defense、それ以外(特殊)はspatk/spdefを使う
    if move.category == CATEGORY_PHYSICAL:
        attack_stat = attacker.status.atk
        defense_stat = defender.status.defense
    else:
        attack_stat = attacker.status.spatk
        defense_stat = defender.status.spdef

        # すなあらしの間、いわタイプの特防は1.5倍になる
        if weather == "sandstorm" and TYPE_ID_ROCK in (defender.type1, defender.type2):
            defense_stat = int(defense_stat * 1.5)

    base_damage = (2 * LEVEL / 5 + 2) * move.power * attack_stat / defense_stat
    base_damage = base_damage / 50 + 2

    # タイプを持たない技(わるあがき等)はタイプ一致による強化(STAB)も無い
    is_stab = not move.is_typeless and resolve_type_id(move.type) in (attacker.type1, attacker.type2)
    stab = 1.5 if is_stab else 1.0

    effectiveness = get_move_effectiveness(move, defender)
    weather_multiplier = get_weather_power_multiplier(move, weather)
    random_factor = random.randint(85, 100) / 100

    crit_chance = HIGH_CRIT_CHANCE if move.high_crit else NORMAL_CRIT_CHANCE
    is_critical = random.random() < crit_chance
    crit_multiplier = CRIT_MULTIPLIER if is_critical else 1.0

    # リフレクター/ひかりのかべによる軽減。急所に当たった場合は壁を無視する
    screen_multiplier = 0.5 if (screen_active and not is_critical) else 1.0

    damage = base_damage * stab * effectiveness * weather_multiplier * crit_multiplier * screen_multiplier * random_factor
    return int(damage)
