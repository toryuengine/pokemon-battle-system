import pytest

from factory import rules


@pytest.mark.parametrize("win_streak, round_number, battle_in_round", [
    (0, 1, 1), (6, 1, 7), (7, 2, 1), (20, 3, 7), (48, 7, 7), (49, 8, 1),
])
def test_round_and_battle_in_round(win_streak, round_number, battle_in_round):
    assert rules.round_of(win_streak) == round_number
    assert rules.battle_in_round_of(win_streak) == battle_in_round


# 6.2 個体値テーブル
@pytest.mark.parametrize("round_number, iv", [
    (1, 0), (2, 4), (3, 8), (4, 12), (5, 16), (6, 20), (7, 24), (8, 31), (20, 31),
])
def test_iv_table(round_number, iv):
    assert rules.iv_for_round(round_number) == iv


# 6.3 強いポケモンの数
@pytest.mark.parametrize("count, strong", [
    (0, 0), (6, 0), (7, 1), (13, 1), (14, 2), (20, 2), (21, 3), (27, 3), (28, 4), (34, 4), (35, 5), (100, 5),
])
def test_strong_rental_count(count, strong):
    assert rules.strong_rental_count(count) == strong


# 9節 BP（シングル）
@pytest.mark.parametrize("round_number, bp", [
    (1, 5), (2, 5), (3, 20), (4, 5), (5, 7), (6, 7), (7, 20), (8, 9), (15, 9),
])
def test_bp_single(round_number, bp):
    assert rules.bp_for_round(round_number) == bp


# 7節 ヒント（シングル）
@pytest.mark.parametrize("round_number, kind", [
    (1, rules.HINT_ALL_NAMES), (2, rules.HINT_TWO_NAMES), (3, rules.HINT_LEAD_AND_MOVE),
    (4, rules.HINT_LEAD_MOVE), (5, rules.HINT_MOST_COMMON_TYPE), (9, rules.HINT_MOST_COMMON_TYPE),
])
def test_hint_kind(round_number, kind):
    assert rules.hint_kind(round_number) == kind


# 6.1 ポケモンプール
def test_pool_spec_lv50():
    assert rules.pool_spec(rules.LEVEL_50, 1).group == 1
    assert rules.pool_spec(rules.LEVEL_50, 2) == rules.PoolSpec(1, (1,), False, rules.GROUP1_RANGE_ROUND2_3)
    assert rules.pool_spec(rules.LEVEL_50, 3).variations == (2,)
    for round_number, variation in ((4, 1), (5, 2), (6, 3), (7, 4)):
        assert rules.pool_spec(rules.LEVEL_50, round_number) == rules.PoolSpec(2, (variation,), False)
    assert rules.pool_spec(rules.LEVEL_50, 8) == rules.PoolSpec(2, None, True)


def test_pool_spec_open():
    for round_number in (1, 2, 3, 4):
        assert rules.pool_spec(rules.LEVEL_OPEN, round_number) == rules.PoolSpec(2, (round_number,), False)
    assert rules.pool_spec(rules.LEVEL_OPEN, 5) == rules.PoolSpec(2, None, True)


# 8節 ネジキ
def test_brain_battles():
    silver = rules.brain_battle(21)
    assert silver.iv == 12 and silver.pool.variations == (1,) and not silver.pool.legendary
    assert silver.print_name == rules.SILVER
    gold = rules.brain_battle(49)
    assert gold.iv == 31 and gold.pool.variations == (4,) and gold.pool.legendary
    assert gold.print_name == rules.GOLD
    for battle_number in (7, 14, 20, 22, 28, 42, 56):
        assert rules.brain_battle(battle_number) is None


def test_type_tiebreak_order_covers_all_types():
    from readpokemondata import load_type_data
    assert set(rules.TYPE_TIEBREAK_ORDER) == set(load_type_data().values())
