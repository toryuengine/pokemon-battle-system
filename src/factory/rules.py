# バトルファクトリー（第4世代・シングル）のルールの表。仕様は「Battle factory gen4 rules.md」の各節
# ここには乱数や対戦エンジンに依存しない、周・連勝数から決まる値だけを置く
from dataclasses import dataclass
from typing import Optional, Tuple

# 挑戦するレベル（2節）。オープンレベルは全ポケモンLv.100
LEVEL_50 = "lv50"
LEVEL_OPEN = "open"
BATTLE_LEVELS = {LEVEL_50: 50, LEVEL_OPEN: 100}

# 1周の対戦数（3節）
BATTLES_PER_ROUND = 7
# 1チームの数・レンタル候補の数（4節）
TEAM_SIZE = 3
RENTAL_CANDIDATES = 6


# 連勝数（これまでに勝った数）から、次の対戦が何周目か（1始まり）
def round_of(win_streak: int) -> int:
    return win_streak // BATTLES_PER_ROUND + 1


# 連勝数から、次の対戦がその周の何戦目か（1〜7）
def battle_in_round_of(win_streak: int) -> int:
    return win_streak % BATTLES_PER_ROUND + 1


# 6.2 個体値テーブル。8周目以降は31
IV_BY_ROUND = {1: 0, 2: 4, 3: 8, 4: 12, 5: 16, 6: 20, 7: 24}
MAX_IV = 31


def iv_for_round(round_number: int) -> int:
    return IV_BY_ROUND.get(round_number, MAX_IV)


# 6.3 強いポケモン（レンタル候補のうち次の周の技構成・個体値で生成される数）
# レンタル＋交換の累計回数（最初のレンタルも1回と数える）が7回ごとに1体増え、最大5体
STRONG_RENTAL_STEP = 7
MAX_STRONG_RENTALS = 5


def strong_rental_count(rent_trade_count: int) -> int:
    return min(rent_trade_count // STRONG_RENTAL_STEP, MAX_STRONG_RENTALS)


# 6.1 ポケモンプール。group=使うリスト、variations=何番目のバリエーションか（Noneなら全バリエーション）、
# legendary=伝説のポケモンを含めるか、species_range=グループ1のうち使う種族の範囲（表示・データ追加用のメモ）
@dataclass(frozen=True)
class PoolSpec:
    group: int
    variations: Optional[Tuple[int, ...]]
    legendary: bool
    species_range: Optional[str] = None


GROUP1_RANGE_ROUND1 = "フシギダネ〜マリルリ"
GROUP1_RANGE_ROUND2_3 = "フシギソウ〜パルシェン"

# Lv.50の周ごとのプール。8周目以降はグループ2の全バリエーション・伝説あり
_POOL_LV50 = {
    1: PoolSpec(group=1, variations=None, legendary=False, species_range=GROUP1_RANGE_ROUND1),
    2: PoolSpec(group=1, variations=(1,), legendary=False, species_range=GROUP1_RANGE_ROUND2_3),
    3: PoolSpec(group=1, variations=(2,), legendary=False, species_range=GROUP1_RANGE_ROUND2_3),
    4: PoolSpec(group=2, variations=(1,), legendary=False),
    5: PoolSpec(group=2, variations=(2,), legendary=False),
    6: PoolSpec(group=2, variations=(3,), legendary=False),
    7: PoolSpec(group=2, variations=(4,), legendary=False),
}
# オープンレベルの周ごとのプール。5周目以降はグループ2の全バリエーション・伝説あり
_POOL_OPEN = {
    1: PoolSpec(group=2, variations=(1,), legendary=False),
    2: PoolSpec(group=2, variations=(2,), legendary=False),
    3: PoolSpec(group=2, variations=(3,), legendary=False),
    4: PoolSpec(group=2, variations=(4,), legendary=False),
}
_POOL_LATE = PoolSpec(group=2, variations=None, legendary=True)


def pool_spec(level: str, round_number: int) -> PoolSpec:
    table = _POOL_LV50 if level == LEVEL_50 else _POOL_OPEN
    return table.get(round_number, _POOL_LATE)


# グループ1のデータがまだ無いので、グループ1を使う周（Lv.50の1〜3周目）はこのグループ2のバリエーションで代用する
# （本編と違う箇所。READMEに記載）。グループ1のデータを足したら使われなくなる
GROUP1_FALLBACK_VARIATIONS = {1: (1,), 2: (1,), 3: (2,)}


# 8節 ファクトリーヘッド・ネジキ（シングルのみ）。連勝21戦目と49戦目（3周目・7周目の7戦目）
@dataclass(frozen=True)
class BrainSpec:
    battle_number: int
    pool: PoolSpec
    iv: int
    # 勝つともらえるプリント
    print_name: str


SILVER = "silver"
GOLD = "gold"
_BRAIN_BATTLES = {
    21: BrainSpec(battle_number=21, pool=PoolSpec(group=2, variations=(1,), legendary=False), iv=12, print_name=SILVER),
    # 伝説のポケモンはどのバリエーションでも使う
    49: BrainSpec(battle_number=49, pool=PoolSpec(group=2, variations=(4,), legendary=True), iv=31, print_name=GOLD),
}


# battle_number（連勝の何戦目か。1始まり）がネジキ戦ならその仕様を返す
def brain_battle(battle_number: int) -> Optional[BrainSpec]:
    return _BRAIN_BATTLES.get(battle_number)


# 9節 周をクリアしたときのBP（シングル）。8周目以降は9
BP_BY_ROUND_SINGLE = {1: 5, 2: 5, 3: 20, 4: 5, 5: 7, 6: 7, 7: 20}
BP_LATE_SINGLE = 9


def bp_for_round(round_number: int) -> int:
    return BP_BY_ROUND_SINGLE.get(round_number, BP_LATE_SINGLE)


# 7節 対戦前ヒント（シングル）の種類
HINT_ALL_NAMES = "all_names"            # 1周目: 3体すべての名前
HINT_TWO_NAMES = "two_names"            # 2周目: 先頭から2体の名前
HINT_LEAD_AND_MOVE = "lead_and_move"    # 3周目: 先発の名前と、その1番目の技
HINT_LEAD_MOVE = "lead_move"            # 4周目: 先発の1番目の技のみ
HINT_MOST_COMMON_TYPE = "most_common_type"  # 5周目以降: 3体で最も多いタイプ

_HINT_BY_ROUND = {1: HINT_ALL_NAMES, 2: HINT_TWO_NAMES, 3: HINT_LEAD_AND_MOVE, 4: HINT_LEAD_MOVE}


def hint_kind(round_number: int) -> str:
    return _HINT_BY_ROUND.get(round_number, HINT_MOST_COMMON_TYPE)


# 「最も多いタイプ」が同数のとき優先するタイプの順（本編のタイプの内部番号順。？？？タイプは除く）
# このリポジトリのタイプID（data/type.json）とは並びが違うので、名前で持つ
TYPE_TIEBREAK_ORDER = ("ノーマル", "かくとう", "ひこう", "どく", "じめん", "いわ", "むし", "ゴースト", "はがね",
                       "ほのお", "みず", "くさ", "でんき", "エスパー", "こおり", "ドラゴン", "あく")
