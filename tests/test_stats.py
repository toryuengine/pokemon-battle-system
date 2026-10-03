import random

import pytest

from nature import NATURES, STAT_KEYS, calc_stat, calc_stats
from pokemon import Pokemon
from readpokemondata import load_pokemon_data


def all_sets():
    for pokemon_id, entry in enumerate(load_pokemon_data()):
        for indivisual_id, set_data in enumerate(entry["indivisual"]):
            yield pokemon_id, indivisual_id, entry, set_data


# 種族値・努力値・性格から計算した実数値が、元データ（Lv.100・個体値0）の実数値と全セットで一致すること
def test_calculated_stats_match_original_data():
    for _, _, entry, set_data in all_sets():
        calculated = calc_stats(entry["base_stats"], set_data["ev"], iv=0, level=100, nature=set_data["nature"])
        assert calculated == {key: set_data["status"][key] for key in STAT_KEYS}, entry["name"]


# フロンティアの努力値は選んだ能力に510を均等に振る形（合計510以下・1能力255以下）
def test_ev_follows_frontier_pattern():
    for _, _, entry, set_data in all_sets():
        values = [value for value in set_data["ev"].values() if value > 0]
        assert len(set(values)) == 1, entry["name"]
        assert values[0] == min(255, 510 // len(values))
        assert set_data["nature"] in NATURES


def test_every_species_has_group2_variations_1_to_4():
    for entry in load_pokemon_data():
        assert [s["variation"] for s in entry["indivisual"]] == [1, 2, 3, 4]
        assert all(s["group"] == 2 for s in entry["indivisual"])


# 実数値の計算式の検算（ガブリアス: 種族値108/130/95/80/85/102、ようき・攻撃と素早さに255）
@pytest.mark.parametrize("level, iv, expected", [
    (50, 31, {"hp": 183, "atk": 182, "def": 115, "spatk": 90, "spdef": 105, "spd": 169}),
    (100, 31, {"hp": 357, "atk": 359, "def": 226, "spatk": 176, "spdef": 206, "spd": 333}),
])
def test_calc_stats_garchomp(level, iv, expected):
    base = {"hp": 108, "atk": 130, "def": 95, "spatk": 80, "spdef": 85, "spd": 102}
    ev = {"hp": 0, "atk": 255, "def": 0, "spatk": 0, "spdef": 0, "spd": 255}
    assert calc_stats(base, ev, iv=iv, level=level, nature="ようき") == expected


def test_neutral_nature_has_no_modifier():
    assert calc_stat("atk", 100, 0, 0, 100, "まじめ") == 205


def test_pokemon_uses_level_and_iv():
    default = Pokemon(0, 0, rng=random.Random(0))
    assert default.level == 100
    assert default.status.hp == load_pokemon_data()[0]["indivisual"][0]["status"]["hp"]

    lv50 = Pokemon(0, 0, level=50, iv=31, rng=random.Random(0))
    assert lv50.level == 50
    assert lv50.status.hp < default.status.hp
    assert lv50.current_status.current_hp == lv50.status.hp


def test_pokemon_rng_makes_gender_and_ability_reproducible():
    first = [(p.gender, p.ability.id) for p in (Pokemon(i, 0, rng=random.Random(42)) for i in range(20))]
    second = [(p.gender, p.ability.id) for p in (Pokemon(i, 0, rng=random.Random(42)) for i in range(20))]
    assert first == second
