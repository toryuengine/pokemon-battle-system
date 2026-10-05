import random

import pytest

from ability.abilityfactory import create_ability
from ability.base_ability import BaseAbility
from battlelogic import battle as battle_module
from battlelogic import damage as damage_module
from battlelogic.battle import Battle
from item.base_item import FLING_POWERS, BaseItem
from item.itemfactory import create_item
from move.base_move import BaseMove
from move.movefactory import create_move
from pokemon import Pokemon
from readpokemondata import (load_ability_data, load_base_stats_data, load_item_data, load_move_data, load_pokemon_data,
                             load_round_data, load_round_pool)


def pokemon_id_of(name):
    return next(i for i, entry in enumerate(load_pokemon_data()) if entry["name"] == name)


# ---- 周ごとのデータ ----

# 周ごとのセット数（pokemon_<周>.jsonに入っているセットの数）
def test_round_pool_sizes():
    assert len(load_round_data()) == 9
    assert [len(load_round_pool(r)) for r in range(9)] == [136, 272, 408, 600, 544, 600, 600, 600, 600]


# 周が進むごとにセットが増えていき、前の周のセットを全て含む（銀ネジキ・5周目以降は全セット）
def test_round_pools_grow():
    pools = [set(load_round_pool(r)) for r in range(9)]
    assert pools[0] < pools[1] < pools[2] < pools[4] < pools[5]
    assert pools[3] == pools[5] == pools[6] == pools[7] == pools[8]


# 伝説のポケモン（14種）は、銀ネジキ・5周目以降の周にだけ出てくる
def test_legendary_rounds():
    legendary_ids = {i for i, entry in enumerate(load_pokemon_data()) if entry["legendary"]}
    assert len(legendary_ids) == 14
    rounds_with_legendary = [r for r in range(9) if any(p in legendary_ids for p, _ in load_round_pool(r))]
    assert rounds_with_legendary == [3, 5, 6, 7, 8]


# 全セットを重複なくまとめたデータ：150種・各4セット
def test_pokemon_data_contains_every_set_once():
    data = load_pokemon_data()
    assert len(data) == 150
    assert all(len(entry["indivisual"]) == 4 for entry in data)
    assert set(load_round_pool(8)) == {(p, s) for p in range(150) for s in range(4)}


# 伝説の種族値は第4世代の値（クレセリアは第9世代で防御・特防が下がっているので、その前の値になっていること）
def test_legendary_base_stats():
    cresselia = load_pokemon_data()[pokemon_id_of("クレセリア")]
    assert cresselia["base_stats"] == {"hp": 120, "atk": 70, "def": 120, "spatk": 75, "spdef": 130, "spd": 85}
    assert cresselia["female_rate"] == 1.0
    assert load_pokemon_data()[pokemon_id_of("レジギガス")]["female_rate"] is None


# 種族値表（data/base_stats.csv → data/base_stats.json）は図鑑番号1〜493の全種族を持つ
def test_base_stats_covers_all_gen4_species():
    data = load_base_stats_data()
    assert sorted(map(int, data)) == list(range(1, 494))
    assert data["1"]["name"] == "フシギダネ" and data["493"]["name"] == "アルセウス"
    # 単タイプはtype2がnull
    assert data["26"]["type2"] is None


# 第6世代以降に種族値が変わった種族は、第4世代の値になっていること
@pytest.mark.parametrize("dex_no, key, expected", [
    ("26", "spd", 100),     # ライチュウ（第6世代で素早さ110）
    ("65", "spdef", 85),    # フーディン（第6世代で特防95）
    ("18", "spd", 91),      # ピジョット（第6世代で素早さ101）
    ("12", "spatk", 80),    # バタフリー（第6世代で特攻90）
])
def test_base_stats_are_gen4_values(dex_no, key, expected):
    assert load_base_stats_data()[dex_no]["base_stats"][key] == expected


# 種族値表に、出てこない種族（ファクトリーのデータに無い進化前など）も入っていること
def test_base_stats_has_species_outside_factory_data():
    factory_dex_numbers = {entry["dex_no"] for entry in load_pokemon_data()}
    assert len(factory_dex_numbers) == 150
    assert len(set(map(int, load_base_stats_data())) - factory_dex_numbers) == 343


# データに出てくる技・特性・持ち物は全て、効果を実装したクラスがある（汎用の基底クラスのままのものが無い）
def test_every_move_ability_item_has_class():
    for move_id, data in load_move_data().items():
        move = create_move(int(move_id))
        assert type(move) is not BaseMove and move.name == data["name"], data["name"]
    for ability_id, name in load_ability_data().items():
        ability = create_ability(int(ability_id))
        assert type(ability) is not BaseAbility and ability.name == name, name
    for item_id, name in load_item_data().items():
        item = create_item(int(item_id))
        assert type(item) is not BaseItem and item.name == name, name


# 全セットのポケモンを作れる
def test_every_set_can_be_created():
    rng = random.Random(0)
    for pokemon_id, entry in enumerate(load_pokemon_data()):
        for indivisual_id in range(len(entry["indivisual"])):
            pokemon = Pokemon(pokemon_id, indivisual_id, level=50, iv=31, rng=rng)
            assert len(pokemon.moves) == 4


# ---- コード中に書いているID（データのIDを振り直したときにずれていないか） ----

def test_move_id_constants():
    names = {move_id: data["name"] for move_id, data in load_move_data().items()}
    assert names[str(battle_module.THUNDER_ID)] == "かみなり"
    assert names[str(battle_module.BLIZZARD_ID)] == "ふぶき"
    assert names[str(battle_module.SOLAR_BEAM_ID)] == "ソーラービーム"
    assert names[str(damage_module.SOLAR_BEAM_ID)] == "ソーラービーム"
    assert names[str(battle_module.BRICK_BREAK_ID)] == "かわらわり"
    assert names[str(battle_module.ENCORE_ID)] == "アンコール"
    assert {names[str(i)] for i in battle_module.PROTECT_FAMILY_MOVE_IDS} == {"こらえる", "まもる", "みきり"}


def test_fling_powers():
    names = load_item_data()
    assert {names[str(item_id)]: power for item_id, power in FLING_POWERS.items()} == {
        "くろいヘドロ": 30, "しんぴのしずく": 30, "かいがらのすず": 30, "いのちのたま": 30, "あついいわ": 60,
        "ひかりのねんど": 30, "おうじゃのしるし": 30, "せんせいのツメ": 80, "するどいツメ": 80, "ねばりのかぎづめ": 90,
        "ふといホネ": 90, "どくどくだま": 30, "くろいてっきゅう": 130, "するどいキバ": 30, "しめったいわ": 60,
        "メトロノーム": 30, "つめたいいわ": 40,
    }


# ---- 新しく増えた技・特性・持ち物 ----

# にぎりつぶす: 威力 = 120 × 相手の残りHP ÷ 相手の最大HP + 1
def test_crush_grip_power():
    move = create_move(270)
    assert move.name == "にぎりつぶす"
    defender = Pokemon(0, 0, rng=random.Random(0))
    assert move.get_power(None, None, defender) == 121
    defender.current_status.current_hp = defender.status.hp // 2
    assert move.get_power(None, None, defender) == 120 * (defender.status.hp // 2) // defender.status.hp + 1
    defender.current_status.current_hp = 1
    assert move.get_power(None, None, defender) == 1


# スロースタート: 場に出てから5ターンの間、攻撃（物理技）と素早さが半分
def test_slow_start():
    regigigas = Pokemon(pokemon_id_of("レジギガス"), 0, rng=random.Random(0))
    assert regigigas.ability.name == "スロースタート"
    battle = Battle(regigigas, Pokemon(0, 0, rng=random.Random(0)))
    regigigas.ability.on_switch_in(battle, regigigas)
    physical = next(m for m in regigigas.moves if m.category == 0)

    slowed_speed = battle.get_effective_speed(regigigas)
    assert regigigas.ability.get_attack_stat_multiplier(regigigas, physical) == 0.5
    for _ in range(5):
        assert battle.get_effective_speed(regigigas) == slowed_speed
        battle.apply_end_of_turn_abilities()
    assert regigigas.ability.get_attack_stat_multiplier(regigigas, physical) == 1.0
    assert battle.get_effective_speed(regigigas) == regigigas.status.spd

    # 交代して出直すと、また5ターン半分になる
    regigigas.ability.on_switch_in(battle, regigigas)
    assert battle.get_effective_speed(regigigas) == slowed_speed


@pytest.mark.parametrize("move_id, name, stat_name", [(267, "ミストボール", "spatk"), (268, "ラスターパージ", "spdef")])
def test_lati_moves_lower_stat(move_id, name, stat_name):
    move = create_move(move_id)
    assert move.name == name
    assert move.effects == [("stat", "target", stat_name, -1, 0.5)]


def test_magma_storm_binds():
    move = create_move(269)
    assert move.name == "マグマストーム"
    assert move.effects == [("bind",)]


def test_charti_berry():
    item = create_item(54)
    assert item.name == "ヨロギのみ"
    assert item.resist_type == "いわ"
