"""バトルファクトリー（第4世代・シングル・オープンレベル）のルールの表。

仕様書（`Battle factory gen4 rules.md`）の表をそのままコードにしたもの。データ（json）には持たず、
ここと tests/test_factory_rules.py で固定する（CLAUDE.md 3.5節）。

周は1始まりの「周の番号」（1周目=1）で扱う。readpokemondata.load_round_pool は0始まりなので、
変換は round_pool_index で行う。
"""
from typing import Optional

# 1周の戦数
BATTLES_PER_ROUND = 7
# 手持ちの数（シングル）
TEAM_SIZE = 3
# レンタル候補の数
RENTAL_CANDIDATE_COUNT = 6
# オープンレベルのポケモンのレベル
OPEN_LEVEL = 100

# 6.2 個体値テーブル：周の番号 → 個体値（全ステータス同じ値）。8周目以降は31
_IV_BY_ROUND = {1: 0, 2: 4, 3: 8, 4: 12, 5: 16, 6: 20, 7: 24}
MAX_IV = 31

# 6.3 強いポケモン：「レンタル＋交換」の累計回数7回ごとに1体増え、最大5体
_TRADES_PER_STRONG_POKEMON = 7
MAX_STRONG_POKEMON = 5

# 9 BP（シングル）：周の番号 → 周クリアでもらえるBP。8周目以降は9
_BP_BY_ROUND = {1: 5, 2: 5, 3: 20, 4: 5, 5: 7, 6: 7, 7: 20}
BP_AFTER_ROUND_7 = 9

# 8 ネジキ戦：連勝の何戦目か（1始まり）→ 種類。"silver"/"gold"はround.jsonの"nejiki"のキー
NEJIKI_BATTLES = {21: "silver", 49: "gold"}
# ネジキ戦の個体値
NEJIKI_IV = {"silver": 12, "gold": 31}

# 7 対戦前ヒント（シングル）の種類
HINT_ALL_NAMES = "all_names"            # 1周目：3体すべての名前
HINT_FIRST_TWO_NAMES = "first_two_names"  # 2周目：先頭から2体の名前
HINT_LEAD_NAME_AND_MOVE = "lead_name_and_move"  # 3周目：先発の名前と、その1番目の技
HINT_LEAD_MOVE = "lead_move"            # 4周目：先発の1番目の技のみ
HINT_MOST_COMMON_TYPE = "most_common_type"  # 5周目以降：3体で最も多いタイプ

# 7 「最も多いタイプ」が同数のときに優先する順（第4世代の内部番号の順）。
# data/type.json のIDとは並びが違うので、タイプ名で対応を取る（？？？タイプはポケモンが持たないので省いている）
TYPE_PRIORITY_NAMES = (
    "ノーマル", "かくとう", "ひこう", "どく", "じめん", "いわ", "むし", "ゴースト", "はがね",
    "ほのお", "みず", "くさ", "でんき", "エスパー", "こおり", "ドラゴン", "あく",
)


# 連勝数（これまでに勝った数）から、次の対戦が何周目か
def round_number_of(win_streak: int) -> int:
    return win_streak // BATTLES_PER_ROUND + 1


# 連勝数から、次の対戦が周の何戦目か（1〜7）
def battle_in_round_of(win_streak: int) -> int:
    return win_streak % BATTLES_PER_ROUND + 1


# 周の番号 → readpokemondata.load_round_pool に渡す番号（0始まり。6周目以降は5周目以降と同じプールになる）
def round_pool_index(round_number: int) -> int:
    if round_number < 1:
        raise ValueError(f"round_number must be 1 or more: {round_number}")
    return round_number - 1


# 6.2 周の番号 → 個体値
def iv_for_round(round_number: int) -> int:
    if round_number < 1:
        raise ValueError(f"round_number must be 1 or more: {round_number}")
    return _IV_BY_ROUND.get(round_number, MAX_IV)


# 6.3 「レンタル＋交換」の累計回数 → レンタル候補6体のうち、次の周の構成・個体値で作る「強いポケモン」の数。
# 累計回数は、今から行うレンタルを含めない回数（最初のレンタルの時点では0。3周目開始時に14回なら2体）
def strong_rental_count(rent_trade_count: int) -> int:
    if rent_trade_count < 0:
        raise ValueError(f"rent_trade_count must not be negative: {rent_trade_count}")
    return min(rent_trade_count // _TRADES_PER_STRONG_POKEMON, MAX_STRONG_POKEMON)


# 9 周の番号 → 周クリアでもらえるBP（シングル）
def bp_for_round(round_number: int) -> int:
    if round_number < 1:
        raise ValueError(f"round_number must be 1 or more: {round_number}")
    return _BP_BY_ROUND.get(round_number, BP_AFTER_ROUND_7)


# 8 連勝の何戦目か（1始まり）→ ネジキ戦なら"silver"/"gold"、そうでなければNone
def nejiki_kind(battle_number: int) -> Optional[str]:
    return NEJIKI_BATTLES.get(battle_number)


# 7 周の番号 → 対戦前ヒントの種類（シングル）
def hint_kind(round_number: int) -> str:
    if round_number < 1:
        raise ValueError(f"round_number must be 1 or more: {round_number}")
    if round_number == 1:
        return HINT_ALL_NAMES
    if round_number == 2:
        return HINT_FIRST_TWO_NAMES
    if round_number == 3:
        return HINT_LEAD_NAME_AND_MOVE
    if round_number == 4:
        return HINT_LEAD_MOVE
    return HINT_MOST_COMMON_TYPE


# 6.4 第何戦かから、相手のポケモンを作るときに使ってよい周の候補（周の番号のリスト）。
# 第1〜6戦は今の周か1つ前の周（1周目は1つ前が無いので1周目だけ）、第7戦は次の周
def opponent_round_candidates(round_number: int, battle_in_round: int) -> list:
    if battle_in_round == BATTLES_PER_ROUND:
        return [round_number + 1]
    if round_number == 1:
        return [1]
    return [round_number, round_number - 1]


# 交換できるのは第1〜6戦の勝利後（第7戦の後は周が終わってレンタルからやり直し）
def can_trade_after(battle_in_round: int) -> bool:
    return battle_in_round < BATTLES_PER_ROUND
