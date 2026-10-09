"""対戦エンジンの既知のバグ（README「既知のバグ」「本編と違う箇所」）を直したときの再現テスト。

ポケモンは make() で作り、技・特性・持ち物をテストごとに必要なものだけにして、他の効果が混ざらないようにする。
"""
import random

import pytest

from ability.abilityfactory import create_ability
from ability.base_ability import NO_ABILITY
from battlelogic import battle as battle_module
from battlelogic import damage as damage_module
from battlelogic.battle import Battle
from battlelogic.damage import calculate_damage, get_weather_power_multiplier
from item.itemfactory import create_item
from move.movefactory import create_move
from pokemon import Pokemon
from readpokemondata import load_ability_data, load_item_data, load_move_data, load_pokemon_data
from trainer import Trainer

TYPE_ID_FLYING = 9
TYPE_ID_STEEL = 16


def pokemon_id_of(name):
    return next(i for i, entry in enumerate(load_pokemon_data()) if entry["name"] == name)


def move_id_of(name):
    return next(int(i) for i, data in load_move_data().items() if data["name"] == name)


def item_id_of(name):
    return next(int(i) for i, item_name in load_item_data().items() if item_name == name)


def ability_id_of(name):
    return next(int(i) for i, ability_name in load_ability_data().items() if ability_name == name)


# 種族名・技名のリストからポケモンを作る。特性は指定しなければ「特性なし」、持ち物は指定しなければ持たない
def make(name, moves, ability=None, item=None, level=50):
    pokemon = Pokemon(pokemon_id_of(name), 0, level=level, iv=31, rng=random.Random(0))
    pokemon.moves = [create_move(move_id_of(move_name)) for move_name in moves]
    pokemon.ability = create_ability(ability_id_of(ability)) if ability is not None else NO_ABILITY
    pokemon.item = create_item(item_id_of(item)) if item is not None else None
    return pokemon


# 1ターンだけ進める
def play_one_turn(battle):
    battle.MAX_TURNS = 1
    battle.start_battle()


# ---- 対戦の進行 ----

# 先攻の攻撃で後攻が瀕死になっても、そのターンのターン終了時の処理（どく・天候ダメージ・天候の残りターン）が行われる。
# 瀕死になった個体の代わりはターン終了時の処理の後に出るので、交代してきた個体は天候ダメージを受けない
def test_end_of_turn_runs_when_second_mover_faints():
    attacker = make("ジュカイン", ["だましうち"])
    attacker.current_status.status_condition = "poison"
    fainting = make("ハガネール", ["だましうち"])
    fainting.current_status.current_hp = 1
    replacement = make("カビゴン", ["だましうち"])
    battle = Battle(Trainer([attacker]), Trainer([fainting, replacement]))
    battle.weather = "sandstorm"
    battle.weather_turns_remaining = 3

    play_one_turn(battle)

    max_hp = attacker.status.hp
    assert attacker.current_status.current_hp == max_hp - max_hp // 8 - max_hp // 16
    assert battle.weather_turns_remaining == 2
    assert battle.pokemon2 is replacement
    assert replacement.current_status.current_hp == replacement.status.hp


# 先攻がいのちのたまの反動で瀕死になっても、代わりの個体はターン終了時まで出てこないので、
# 後攻の技は対象がいなくて失敗する（交代してきた個体に当たらない）
def test_replacement_is_not_hit_after_self_faint():
    attacker = make("ジュカイン", ["だましうち"], item="いのちのたま")
    attacker.current_status.current_hp = 1
    replacement = make("カビゴン", ["だましうち"])
    defender = make("ハガネール", ["だましうち"])
    battle = Battle(Trainer([attacker, replacement]), Trainer([defender]))

    play_one_turn(battle)

    assert attacker.current_status.current_hp == 0
    assert battle.pokemon1 is replacement
    assert replacement.current_status.current_hp == replacement.status.hp


# おいうちで瀕死になった個体は交代せず、代わりはターン終了時に出る
def test_pursuit_faint_defers_replacement():
    switcher = make("ムウマージ", ["だましうち"])
    switcher.current_status.current_hp = 1
    bench = make("カビゴン", ["だましうち"])
    pursuer = make("ハガネール", [load_move_data()[str(move_id)]["name"] for move_id in [_pursuit_id()]])
    trainer1 = Trainer([switcher, bench], switch_policy=lambda battle, trainer: 1)
    battle = Battle(trainer1, Trainer([pursuer]))

    play_one_turn(battle)

    assert switcher.current_status.current_hp == 0
    assert battle.pokemon1 is bench


def _pursuit_id():
    return move_id_of("おいうち")


# たいねつのやけどダメージは最大HPの1/32だけ（通常の1/16が重ねて掛からない）
def test_heatproof_burn_damage_is_not_doubled():
    bronzong = make("ドータクン", ["だましうち"], ability="たいねつ")
    battle = Battle(bronzong, make("カビゴン", ["だましうち"]))
    bronzong.current_status.status_condition = "burn"

    battle.apply_end_of_turn_status_damage()

    assert bronzong.status.hp - bronzong.current_status.current_hp == bronzong.status.hp // 32


# ねむりで行動できないターン数は1〜4（第4世代）
def test_sleep_turns_are_one_to_four():
    random.seed(0)
    seen = set()
    for _ in range(200):
        target = make("カビゴン", ["だましうち"])
        battle = Battle(make("ハガネール", ["だましうち"]), target)
        battle.try_apply_status(target, "sleep", 1.0)
        seen.add(target.current_status.sleep_turns_remaining)
    assert seen == {1, 2, 3, 4}


# まもるの連続成功率は1/2ずつ下がり、1/8で下げ止まる
@pytest.mark.parametrize("stall_count, roll, succeeds", [
    (1, 0.49, True), (1, 0.51, False),
    (2, 0.24, True), (2, 0.26, False),
    (5, 0.12, True), (5, 0.13, False),
])
def test_protect_success_chance(monkeypatch, stall_count, roll, succeeds):
    user = make("カビゴン", ["まもる"])
    battle = Battle(user, make("ハガネール", ["だましうち"]))
    user.current_status.protect_stall_counter = stall_count
    monkeypatch.setattr(battle_module.random, "random", lambda: roll)
    battle.perform_protect(user)
    assert user.current_status.is_protected is succeeds


# 一撃必殺技の命中率は「30＋レベル差」で、ランク補正を受けず、相手の方がレベルが高いと必ず失敗する
def test_ohko_accuracy_uses_level_difference():
    attacker = make("ハガネール", ["じわれ"], level=60)
    defender = make("カビゴン", ["だましうち"], level=50)
    battle = Battle(attacker, defender)
    fissure = attacker.moves[0]
    assert battle.get_effective_hitrate(fissure, attacker, defender) == 40
    battle.stages1.accuracy = -6
    battle.stages2.evasion = 6
    assert battle.get_effective_hitrate(fissure, attacker, defender) == 40


def test_ohko_fails_against_higher_level(monkeypatch):
    attacker = make("ハガネール", ["じわれ"], ability="ノーガード", level=50)
    defender = make("カビゴン", ["だましうち"], level=51)
    battle = Battle(attacker, defender)
    result = battle.use_move(attacker, defender, attacker.moves[0])
    assert not result["hit"]
    assert defender.current_status.current_hp == defender.status.hp


# こおり状態の相手は、ほのお技を受けると解ける
def test_fire_move_thaws_target(monkeypatch):
    attacker = make("ゴウカザル", ["かえんほうしゃ"])
    defender = make("カビゴン", ["だましうち"])
    battle = Battle(attacker, defender)
    defender.current_status.status_condition = "freeze"
    monkeypatch.setattr(battle_module.random, "random", lambda: 0.99)  # やけどの追加効果を出さない
    battle.use_move(attacker, defender, attacker.moves[0])
    assert defender.current_status.status_condition is None


# にほんばれの間はこおり状態にならない
def test_no_freeze_in_sun():
    target = make("カビゴン", ["だましうち"])
    battle = Battle(make("ハガネール", ["だましうち"]), target)
    battle.weather = "sun"
    assert not battle.try_apply_status(target, "freeze", 1.0)
    assert target.current_status.status_condition is None


# フレアドライブはこおり状態でも使え、自分のこおりが解ける
def test_flare_blitz_thaws_user(monkeypatch):
    user = make("ゴウカザル", ["フレアドライブ"])
    battle = Battle(user, make("カビゴン", ["だましうち"]))
    user.current_status.status_condition = "freeze"
    monkeypatch.setattr(battle_module.random, "random", lambda: 0.99)  # 自然には解けない
    assert battle.can_act(user, user.moves[0])
    assert user.current_status.status_condition is None


# ソーラービームの威力は、雨・すなあらし・あられで半分になる
@pytest.mark.parametrize("weather, multiplier", [
    (None, 1.0), ("sun", 1.0), ("rain", 0.5), ("sandstorm", 0.5), ("hail", 0.5),
])
def test_solar_beam_weather_power(weather, multiplier):
    assert get_weather_power_multiplier(create_move(move_id_of("ソーラービーム")), weather) == multiplier


# そらをとぶ・ダイビング・あなをほるの最中に当たる技と、威力が2倍になる技
@pytest.mark.parametrize("move_name, charging_name, doubled", [
    ("かみなり", "そらをとぶ", False),
    ("たつまき", "そらをとぶ", True),
    ("うずしお", "ダイビング", True),
    ("じわれ", "あなをほる", False),
])
def test_moves_hitting_charging_target(move_name, charging_name, doubled):
    move = create_move(move_id_of(move_name))
    defender = make("カビゴン", ["だましうち"])
    battle = Battle(make("ハガネール", ["だましうち"]), defender)
    defender.current_status.charging_move = create_move(move_id_of(charging_name))
    defender.current_status.is_invulnerable = True
    assert battle.hits_charging_target(move, defender)
    if not move.is_ohko:
        assert move.get_power(battle, None, defender) == move.power * (2 if doubled else 1)


# ---- 技のデータ ----

def test_shock_wave_has_no_paralysis():
    move = create_move(move_id_of("でんげきは"))
    assert move.effects == []
    assert move.hitrate == 0


def test_volt_tackle_paralysis():
    assert ("status", "target", "paralysis", 0.1) in create_move(move_id_of("ボルテッカー")).effects


def test_blaze_kick_high_crit():
    assert create_move(move_id_of("ブレイズキック")).high_crit


@pytest.mark.parametrize("move_name, priority", [
    ("こらえる", 3), ("しんそく", 1), ("こおりのつぶて", 1), ("ふいうち", 1), ("だましうち", 0),
])
def test_priorities(move_name, priority):
    assert create_move(move_id_of(move_name)).priority == priority


@pytest.mark.parametrize("move_name, contact", [
    ("こおりのつぶて", False), ("くさむすび", True), ("しぼりとる", True), ("にぎりつぶす", True),
])
def test_contact(move_name, contact):
    assert create_move(move_id_of(move_name)).makes_contact is contact


# はねやすめを使ったターンの間はひこうタイプが無くなり、ターンの終わりに戻る。HPが満タンなら失敗する
def test_roost_removes_flying_type_for_the_turn():
    skarmory = make("エアームド", ["はねやすめ"])
    battle = Battle(skarmory, make("カビゴン", ["だましうち"]))
    skarmory.current_status.current_hp = 1

    battle.use_move(skarmory, battle.pokemon2, skarmory.moves[0])
    assert (skarmory.type1, skarmory.type2) == (TYPE_ID_STEEL, None)
    assert skarmory.current_status.current_hp == 1 + skarmory.status.hp // 2

    battle.process_end_of_turn()
    assert (skarmory.type1, skarmory.type2) == (TYPE_ID_STEEL, TYPE_ID_FLYING)

    skarmory.current_status.current_hp = skarmory.status.hp
    battle.use_move(skarmory, battle.pokemon2, skarmory.moves[0])
    assert TYPE_ID_FLYING in (skarmory.type1, skarmory.type2)


# くさむすびの威力は相手の体重で決まる
@pytest.mark.parametrize("name, power", [("ムウマージ", 20), ("ライチュウ", 60), ("カビゴン", 120), ("ジュゴン", 100)])
def test_grass_knot_power_by_weight(name, power):
    assert create_move(move_id_of("くさむすび")).get_power(None, None, make(name, ["だましうち"])) == power


# ---- 本編と違っていた技 ----

# ふいうち: 相手が攻撃技を選んでいて、まだ行動していなければ成功する
@pytest.mark.parametrize("selected, has_moved, succeeds", [
    ("だましうち", False, True),
    ("まもる", False, False),
    (None, False, False),
    ("だましうち", True, False),
])
def test_sucker_punch_conditions(selected, has_moved, succeeds):
    attacker = make("アブソル", ["ふいうち"])
    defender = make("カビゴン", ["だましうち", "まもる"])
    battle = Battle(attacker, defender)
    defender.current_status.selected_move_this_turn = (
        next(m for m in defender.moves if m.name == selected) if selected is not None else None)
    defender.current_status.has_moved_this_turn = has_moved
    result = battle.use_move(attacker, defender, attacker.moves[0])
    assert result["hit"] is succeeds


# がむしゃら: 相手の残りHPを自分の残りHPと同じにする。自分の方がHPが多ければ失敗し、ゴーストタイプには当たらない
def test_endeavor():
    attacker = make("カビゴン", ["がむしゃら"])
    defender = make("ハガネール", ["だましうち"])
    battle = Battle(attacker, defender)
    attacker.current_status.current_hp = 10
    battle.use_move(attacker, defender, attacker.moves[0])
    assert defender.current_status.current_hp == 10

    attacker.current_status.current_hp = 50
    result = battle.use_move(attacker, defender, attacker.moves[0])
    assert not result["hit"]
    assert defender.current_status.current_hp == 10

    ghost = make("ムウマージ", ["だましうち"])
    battle = Battle(attacker, ghost)
    attacker.current_status.current_hp = 1
    battle.use_move(attacker, ghost, attacker.moves[0])
    assert ghost.current_status.current_hp == ghost.status.hp


# ---- 細かいもの ----

# ダメージは第4世代の式の順番どおりに、補正のたびに切り捨てる
def test_damage_formula_rounding(monkeypatch):
    attacker = make("ゴウカザル", ["かえんほうしゃ"])
    defender = make("ハガネール", ["だましうち"])
    move = attacker.moves[0]
    monkeypatch.setattr(damage_module.random, "randint", lambda low, high: 100)
    damage = calculate_damage(attacker, defender, move, weather="sun", is_critical=False)

    expected = (2 * 50 // 5 + 2) * move.power * attacker.status.spatk // 50 // defender.status.spdef
    expected = int(expected * 1.5) + 2  # 晴れ
    expected = int(expected * 1.5)  # タイプ一致
    expected = int(int(expected * 2) * 1)  # はがね×2、じめん×1
    assert damage == expected


# 瀕死の相手には状態異常・能力ランクの変化・ひるみが付かない
def test_no_effects_on_fainted_target():
    target = make("カビゴン", ["だましうち"])
    source = make("ハガネール", ["だましうち"])
    battle = Battle(source, target)
    target.current_status.current_hp = 0
    assert not battle.try_apply_status(target, "paralysis", 1.0, source=source)
    assert not battle.try_apply_stat_change(target, "atk", -1, 1.0, source=source)
    assert not battle.try_apply_flinch(target, 1.0, source=source)
    assert target.current_status.status_condition is None
