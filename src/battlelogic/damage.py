import random

from ability.base_ability import NO_ABILITY
from battlelogic.stat_stage import stage_multiplier
from battlelogic.type_chart import get_move_effectiveness, resolve_type_id
from move.base_move import CATEGORY_PHYSICAL, CATEGORY_STATUS

# jsonの実数値にレベルが織り込まれておらず、データ上レベルを特定できないため
# 便宜上レベル100固定で計算する（両者同条件なので相対的なダメージ比較には影響しない）
LEVEL = 100

# 急所ランクごとの急所の発生率（第4世代仕様）。通常は1/16、急所に当たりやすい技(high_crit)や
# ピントレンズ等の持ち物でランクが1つずつ上がる（4以上は1/2で頭打ち）
CRIT_CHANCE_BY_STAGE = [1 / 16, 1 / 8, 1 / 4, 1 / 3, 1 / 2]
# 第4世代の急所ダメージ倍率（第6世代以降の1.5倍とは異なる）
CRIT_MULTIPLIER = 2.0

TYPE_ID_ROCK = 12

# ソーラービームのid。晴れ以外での溜め省略・雨での威力半減という固有仕様があるため個別に参照する
SOLAR_BEAM_ID = 19

# じたばた等、自分の残りHP割合によって威力が変わる技の閾値テーブル
# (残りHP割合の下限(以上), 威力)。上から順に見て、最初に条件を満たしたものを使う
HP_BASED_POWER_TABLE = [
    (0.6875, 20),
    (0.3542, 40),
    (0.1563, 80),
    (0.0938, 100),
    (0.0417, 150),
    (0.0, 200),
]


# attackerの残りHP割合から、上のテーブルに沿った威力を返す
def get_hp_based_power(attacker) -> int:
    hp_ratio = attacker.current_status.current_hp / attacker.status.hp
    for threshold, power in HP_BASED_POWER_TABLE:
        if hp_ratio >= threshold:
            return power
    return HP_BASED_POWER_TABLE[-1][1]


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


# 能力ランクを実数値に反映する。急所に当たった場合、攻撃側の下降ランク・防御側の上昇ランクは無視する（第4世代仕様）
def apply_stage_to_stat(stat: int, stage: int, is_critical: bool, is_attack_side: bool) -> int:
    if is_critical:
        if is_attack_side and stage < 0:
            stage = 0
        if not is_attack_side and stage > 0:
            stage = 0
    return int(stat * stage_multiplier(stage))


# こんらんの自傷ダメージ（第4世代仕様）。威力40・タイプなしの物理技で自分自身を攻撃した扱いになり、
# 自分の攻撃・防御の実数値とランク補正を使う。急所・タイプ一致・タイプ相性・天候・壁の影響は受けず、乱数(85〜100%)のみ掛かる
CONFUSION_SELF_HIT_POWER = 40


def calculate_confusion_damage(pokemon, stages=None) -> int:
    attack_stat = apply_stage_to_stat(pokemon.status.atk, stages.atk if stages else 0, False, is_attack_side=True)
    defense_stat = max(1, apply_stage_to_stat(pokemon.status.defense, stages.defense if stages else 0, False, is_attack_side=False))

    base_damage = (2 * LEVEL / 5 + 2) * CONFUSION_SELF_HIT_POWER * attack_stat / defense_stat
    base_damage = base_damage / 50 + 2

    random_factor = random.randint(85, 100) / 100
    return max(1, int(base_damage * random_factor))


# 急所ランクから急所の発生率を返す
def get_crit_chance(crit_stage: int) -> float:
    return CRIT_CHANCE_BY_STAGE[min(crit_stage, len(CRIT_CHANCE_BY_STAGE) - 1)]


# 急所に当たるかどうかを判定する。急所ランクは技(high_crit)・持ち物・特性（きょううん）で上がり、
# 受ける側の特性がカブトアーマー・シェルアーマーなら急所に当たらない
def roll_critical(attacker, move, attacker_ability=NO_ABILITY, defender_ability=NO_ABILITY) -> bool:
    if defender_ability.prevents_critical_hit:
        return False
    crit_stage = ((1 if move.high_crit else 0) + attacker.held_item.get_crit_stage_bonus(attacker)
                  + attacker_ability.crit_stage_bonus)
    return random.random() < get_crit_chance(crit_stage)


# attacker_stages/defender_stagesは両者のStatStages。省略時はランク補正なし（0段階）として計算する
# attacker側の持ち物の効果（ちからのハチマキ・こだわりハチマキ・いのちのたま・メトロノーム等）はここで反映する。
# 半減実のように発動すると消費される（Battle側で状態を変える必要がある）倍率は、Battle側からextra_multiplierで渡す
# attacker_ability/defender_abilityは両者の特性（いえきで消されている・かたやぶりで無視される場合はNO_ABILITY）。
# is_criticalを省略すると、ここで急所判定を行う（Battle側はいかりのつぼの判定のため、事前にroll_criticalで決めて渡す）
# battleは状況によって威力が変わる技（しおみず・しっぺがえし等）の威力判定に使う。省略時は技の基本の威力で計算する
def calculate_damage(attacker, defender, move, weather=None, screen_active=False, ignore_ghost_immunity=False,
                     attacker_stages=None, defender_stages=None, extra_multiplier=1.0,
                     attacker_ability=NO_ABILITY, defender_ability=NO_ABILITY, is_critical=None, battle=None) -> int:
    # 変化技(CATEGORY_STATUS)はダメージを与えない
    if move.category == CATEGORY_STATUS:
        return 0

    # 一撃必殺技: タイプ相性が0倍(無効)なら失敗、それ以外は相手の残りHPと同じ量のダメージで即座に瀕死にする
    if move.is_ohko:
        if get_move_effectiveness(move, defender, ignore_ghost_immunity) == 0:
            return 0
        return defender.current_status.current_hp

    # 急所判定はランク補正の扱いに影響するため、実数値を決める前に行う
    attacker_item = attacker.held_item
    if is_critical is None:
        is_critical = roll_critical(attacker, move, attacker_ability, defender_ability)

    # 物理技(CATEGORY_PHYSICAL)はatk/defense、それ以外(特殊)はspatk/spdefを使う
    if move.category == CATEGORY_PHYSICAL:
        attack_stat = attacker.status.atk
        defense_stat = defender.status.defense
        attack_stage = attacker_stages.atk if attacker_stages else 0
        defense_stage = defender_stages.defense if defender_stages else 0
    else:
        attack_stat = attacker.status.spatk
        defense_stat = defender.status.spdef
        attack_stage = attacker_stages.spatk if attacker_stages else 0
        defense_stage = defender_stages.spdef if defender_stages else 0

    attack_stat = apply_stage_to_stat(attack_stat, attack_stage, is_critical, is_attack_side=True)
    attack_stat = int(attack_stat * attacker_item.get_attack_stat_multiplier(attacker, move))
    attack_stat = int(attack_stat * attacker_ability.get_attack_stat_multiplier(attacker, move))
    defense_stat = max(1, apply_stage_to_stat(defense_stat, defense_stage, is_critical, is_attack_side=False))
    defense_stat = max(1, int(defense_stat * defender_ability.get_defense_stat_multiplier(defender, move)))

    # だいばくはつは相手の防御を半分にして計算する（第4世代仕様）
    if move.halves_target_defense:
        defense_stat = max(1, defense_stat // 2)

    # すなあらしの間、いわタイプの特防は1.5倍になる
    if move.category != CATEGORY_PHYSICAL and weather == "sandstorm" and TYPE_ID_ROCK in (defender.type1, defender.type2):
        defense_stat = int(defense_stat * 1.5)

    power = get_hp_based_power(attacker) if move.has_hp_based_power else move.get_power(battle, attacker, defender)
    # テクニシャン等は持ち物・じゅうでんの補正前の威力で判定する
    ability_power_multiplier = (attacker_ability.get_power_multiplier(attacker, move, power)
                                * defender_ability.get_received_power_multiplier(defender, move))

    # じゅうでん状態なら、でんき技の威力が2倍になる
    if attacker.current_status.charge_turns_remaining > 0 and move.type == "でんき":
        power *= 2

    power = int(power * attacker_item.get_power_multiplier(attacker, move) * ability_power_multiplier)

    base_damage = (2 * LEVEL / 5 + 2) * power * attack_stat / defense_stat
    base_damage = base_damage / 50 + 2

    # タイプを持たない技(わるあがき等)はタイプ一致による強化(STAB)も無い
    is_stab = not move.is_typeless and resolve_type_id(move.type) in (attacker.type1, attacker.type2)
    stab = attacker_ability.stab_multiplier if is_stab else 1.0

    effectiveness = get_move_effectiveness(move, defender, ignore_ghost_immunity)
    weather_multiplier = get_weather_power_multiplier(move, weather)
    random_factor = random.randint(85, 100) / 100

    crit_multiplier = CRIT_MULTIPLIER * attacker_ability.critical_multiplier_bonus if is_critical else 1.0

    # リフレクター/ひかりのかべによる軽減。急所に当たった場合は壁を無視する
    screen_multiplier = 0.5 if (screen_active and not is_critical) else 1.0

    item_multiplier = attacker_item.get_damage_multiplier(attacker, effectiveness) * extra_multiplier
    ability_multiplier = (attacker_ability.get_damage_multiplier(attacker, move, effectiveness)
                          * defender_ability.get_received_damage_multiplier(defender, move, effectiveness))

    damage = (base_damage * stab * effectiveness * weather_multiplier * crit_multiplier * screen_multiplier
              * item_multiplier * ability_multiplier * random_factor)
    return int(damage)
