"""バトルファクトリーのルールの表（仕様書6.2・6.3・7・8・9節）を固定するテスト。"""
import pytest

from factory import rules
from readpokemondata import load_type_data


# 6.2 個体値テーブル
@pytest.mark.parametrize("round_number, iv", [
    (1, 0), (2, 4), (3, 8), (4, 12), (5, 16), (6, 20), (7, 24), (8, 31), (9, 31), (20, 31),
])
def test_iv_for_round(round_number, iv):
    assert rules.iv_for_round(round_number) == iv


# 6.3 強いポケモンの数（今から行うレンタルを含めない累計回数で数える）
@pytest.mark.parametrize("count, strong", [
    (0, 0), (6, 0), (7, 1), (13, 1), (14, 2), (20, 2), (21, 3), (27, 3), (28, 4), (34, 4), (35, 5), (100, 5),
])
def test_strong_rental_count(count, strong):
    assert rules.strong_rental_count(count) == strong


# 仕様書の例：3周目開始時点で累計14回なら2体（1周目・2周目で6回ずつ交換した場合、レンタル2回＋交換12回）
def test_strong_rental_count_example():
    assert rules.strong_rental_count(1 + 6 + 1 + 6) == 2


# 9 BP（シングル）
@pytest.mark.parametrize("round_number, bp", [
    (1, 5), (2, 5), (3, 20), (4, 5), (5, 7), (6, 7), (7, 20), (8, 9), (9, 9), (15, 9),
])
def test_bp_for_round(round_number, bp):
    assert rules.bp_for_round(round_number) == bp


# 7 対戦前ヒントの種類（シングル）
@pytest.mark.parametrize("round_number, kind", [
    (1, rules.HINT_ALL_NAMES), (2, rules.HINT_FIRST_TWO_NAMES), (3, rules.HINT_LEAD_NAME_AND_MOVE),
    (4, rules.HINT_LEAD_MOVE), (5, rules.HINT_MOST_COMMON_TYPE), (8, rules.HINT_MOST_COMMON_TYPE),
])
def test_hint_kind(round_number, kind):
    assert rules.hint_kind(round_number) == kind


# 8 ネジキ戦は21戦目（銀・個体値12）と49戦目（金・個体値31）だけ
@pytest.mark.parametrize("battle_number, kind", [
    (21, "silver"), (49, "gold"), (7, None), (14, None), (20, None), (22, None), (28, None), (42, None), (56, None),
    (70, None),
])
def test_nejiki_kind(battle_number, kind):
    assert rules.nejiki_kind(battle_number) == kind


def test_nejiki_iv():
    assert rules.NEJIKI_IV == {"silver": 12, "gold": 31}


# 12 連勝数 → 周・周の何戦目か
@pytest.mark.parametrize("win_streak, round_number, battle_in_round", [
    (0, 1, 1), (6, 1, 7), (7, 2, 1), (20, 3, 7), (21, 4, 1), (48, 7, 7), (49, 8, 1),
])
def test_round_and_battle_of_streak(win_streak, round_number, battle_in_round):
    assert rules.round_number_of(win_streak) == round_number
    assert rules.battle_in_round_of(win_streak) == battle_in_round


# ネジキ戦は3周目・7周目の第7戦
def test_nejiki_battles_are_seventh_of_round_3_and_7():
    assert (rules.round_number_of(20), rules.battle_in_round_of(20)) == (3, 7)
    assert (rules.round_number_of(48), rules.battle_in_round_of(48)) == (7, 7)


# 6.4 相手のポケモンの周：第1〜6戦は今の周か1つ前の周、第7戦は次の周
@pytest.mark.parametrize("round_number, battle_in_round, candidates", [
    (1, 1, [1]), (1, 6, [1]), (1, 7, [2]), (2, 1, [2, 1]), (5, 6, [5, 4]), (5, 7, [6]),
])
def test_opponent_round_candidates(round_number, battle_in_round, candidates):
    assert rules.opponent_round_candidates(round_number, battle_in_round) == candidates


# 交換できるのは第1〜6戦の勝利後だけ
def test_can_trade_after():
    assert all(rules.can_trade_after(battle) for battle in range(1, 7))
    assert not rules.can_trade_after(7)


# 「最も多いタイプ」の優先順は、data/type.json の全タイプを含む
def test_type_priority_covers_all_types():
    assert set(load_type_data().values()) == set(rules.TYPE_PRIORITY_NAMES)
    assert len(rules.TYPE_PRIORITY_NAMES) == 17


@pytest.mark.parametrize("function", [rules.iv_for_round, rules.bp_for_round, rules.hint_kind, rules.round_pool_index])
def test_round_number_starts_at_one(function):
    with pytest.raises(ValueError):
        function(0)
