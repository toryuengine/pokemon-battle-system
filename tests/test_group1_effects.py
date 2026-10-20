"""グループ1で使われる技・持ち物・特性（こうそくスピン・しんぴのまもり・とびはねる・あかいいと・マジックガード・やるき）のテスト。

ポケモンは make() で作り、技・特性・持ち物をテストごとに必要なものだけにして、他の効果が混ざらないようにする。
"""
import random

import pytest

from ability.abilityfactory import create_ability
from ability.base_ability import NO_ABILITY
from battlelogic.battle import Battle
from item.itemfactory import create_item
from move.movefactory import create_move
from move.struggle import Struggle
from pokemon import Pokemon
from readpokemondata import load_ability_data, load_item_data, load_move_data, load_pokemon_data
from trainer import Trainer


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


def damage_taken(pokemon):
    return pokemon.status.hp - pokemon.current_status.current_hp


# ---- 技のデータ ----

@pytest.mark.parametrize("name, move_type, category, power, hitrate, pp, contact", [
    ("こうそくスピン", "ノーマル", 0, 20, 100, 40, True),
    ("しんぴのまもり", "ノーマル", 2, 0, 0, 25, False),
    ("とびはねる", "ひこう", 0, 85, 85, 5, True),
])
def test_move_data(name, move_type, category, power, hitrate, pp, contact):
    move = create_move(move_id_of(name))
    assert (move.name, move.type, move.category, move.power, move.hitrate, move.pp, move.makes_contact) == \
        (name, move_type, category, power, hitrate, pp, contact)


# ---- こうそくスピン ----

# 自分の場の罠と、自分にかかっているやどりぎのタネ・しめつけを取り除く（相手の場の罠はそのまま）
def test_rapid_spin_clears_hazards_and_traps(monkeypatch):
    monkeypatch.setattr("battlelogic.accuracy.random.randint", lambda a, b: 1)
    spinner = make("フォレトス", ["こうそくスピン"])
    opponent = make("カビゴン", ["だましうち"])
    battle = Battle(spinner, opponent)
    battle.trainer1.stealth_rock = True
    battle.trainer1.spikes = 3
    battle.trainer1.toxic_spikes = 2
    battle.trainer2.spikes = 1
    spinner.current_status.is_seeded = True
    spinner.current_status.bound_turns_remaining = 3
    spinner.current_status.bound_by = opponent

    result = battle.use_move(spinner, opponent, spinner.moves[0])

    assert result["hit"]
    assert (battle.trainer1.stealth_rock, battle.trainer1.spikes, battle.trainer1.toxic_spikes) == (False, 0, 0)
    assert not spinner.current_status.is_seeded
    assert spinner.current_status.bound_turns_remaining == 0 and spinner.current_status.bound_by is None
    assert battle.trainer2.spikes == 1


# ゴーストタイプには当たらないので、罠は取り除けない
def test_rapid_spin_fails_against_ghost():
    spinner = make("フォレトス", ["こうそくスピン"])
    battle = Battle(spinner, make("ゲンガー", ["だましうち"]))
    battle.trainer1.stealth_rock = True

    battle.use_move(spinner, battle.pokemon2, spinner.moves[0])

    assert battle.trainer1.stealth_rock


# ---- しんぴのまもり ----

# 使ったターンを含めて5ターン続き、効果中にもう一度使うと失敗する（残りターンは延びない）
def test_safeguard_duration():
    user = make("カビゴン", ["しんぴのまもり"])
    battle = Battle(user, make("ハガネール", ["だましうち"]))

    battle.use_move(user, battle.pokemon2, user.moves[0])
    assert battle.trainer1.safeguard_turns_remaining == 5
    battle.tick_screens()
    battle.use_move(user, battle.pokemon2, user.moves[0])
    assert battle.trainer1.safeguard_turns_remaining == 4
    for _ in range(4):
        battle.tick_screens()
    assert not battle.is_safeguarded(user)


# 相手の技による状態異常・こんらん・あくびを防ぐ
@pytest.mark.parametrize("move_name", ["でんじは", "あやしいひかり", "あくび", "どくどく"])
def test_safeguard_blocks_opponent_moves(move_name):
    protected = make("カビゴン", ["だましうち"])
    attacker = make("スターミー", [move_name])
    battle = Battle(protected, attacker)
    battle.set_safeguard(battle.trainer1)

    battle.use_move(attacker, protected, attacker.moves[0])

    status = protected.current_status
    assert status.status_condition is None
    assert status.confusion_turns_remaining == 0
    assert status.yawn_turns_remaining == 0


# 自分で起こす状態異常（ねむる・げきりんの後のこんらん・ねむけが進んでねむる）は防がない
def test_safeguard_does_not_block_self_inflicted():
    user = make("カビゴン", ["ねむる"])
    battle = Battle(user, make("ハガネール", ["だましうち"]))
    battle.set_safeguard(battle.trainer1)

    user.current_status.current_hp = 1
    battle.use_move(user, battle.pokemon2, user.moves[0])
    assert user.current_status.status_condition == "sleep"

    battle.cure_status(user)
    assert battle.try_apply_status(user, "confusion", 1.0)

    # しんぴのまもりを張る前からねむけ状態なら、そのままねむる
    battle.cure_status(user)
    user.current_status.yawn_turns_remaining = 1
    battle.tick_volatile_statuses()
    assert user.current_status.status_condition == "sleep"


# どくびし・どくどくだまでもどくにならない（第4世代）
def test_safeguard_blocks_toxic_spikes_and_toxic_orb():
    holder = make("カビゴン", ["だましうち"], item="どくどくだま")
    bench = make("カビゴン", ["だましうち"])
    battle = Battle(Trainer([holder, bench]), Trainer([make("ハガネール", ["だましうち"])]))
    battle.set_safeguard(battle.trainer1)

    battle.apply_end_of_turn_orbs()
    assert holder.current_status.status_condition is None

    battle.trainer1.toxic_spikes = 2
    battle.switch_in(battle.trainer1, 1)
    assert bench.current_status.status_condition is None


# 第4世代では、せいでんき等の接触技を受けて発動する特性は防げない
def test_safeguard_does_not_block_contact_abilities(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.0)
    attacker = make("カビゴン", ["だましうち"])
    static = make("ハガネール", ["だましうち"], ability="せいでんき")
    battle = Battle(attacker, static)
    battle.set_safeguard(battle.trainer1)

    battle.use_move(attacker, static, attacker.moves[0])

    assert attacker.current_status.status_condition == "paralysis"


# シンクロで相手にうつす状態異常も防ぐ
def test_safeguard_blocks_synchronize():
    attacker = make("カビゴン", ["でんじは"])
    synchronizer = make("スターミー", ["だましうち"], ability="シンクロ")
    battle = Battle(attacker, synchronizer)
    battle.set_safeguard(battle.trainer1)

    battle.use_move(attacker, synchronizer, attacker.moves[0])

    assert synchronizer.current_status.status_condition == "paralysis"
    assert attacker.current_status.status_condition is None


# ---- とびはねる ----

# 1ターン目は跳び上がって回避状態になり、ふつうの技は当たらない
def test_bounce_charge_turn_is_invulnerable():
    bouncer = make("カビゴン", ["とびはねる"])
    attacker = make("ハガネール", ["だましうち"])
    battle = Battle(bouncer, attacker)

    result = battle.use_move(bouncer, attacker, bouncer.moves[0])
    assert result["charging"] and bouncer.current_status.is_invulnerable

    assert not battle.use_move(attacker, bouncer, attacker.moves[0])["hit"]
    assert bouncer.current_status.current_hp == bouncer.status.hp


# かみなり・たつまき・スカイアッパーは、とびはねるで上空にいる相手にも当たる（たつまきだけ威力2倍）
@pytest.mark.parametrize("move_name, doubled", [("かみなり", False), ("たつまき", True), ("スカイアッパー", False)])
def test_moves_hitting_bounce(move_name, doubled):
    move = create_move(move_id_of(move_name))
    defender = make("カビゴン", ["だましうち"])
    battle = Battle(make("ハガネール", ["だましうち"]), defender)
    defender.current_status.charging_move = create_move(move_id_of("とびはねる"))
    defender.current_status.is_invulnerable = True
    assert battle.hits_charging_target(move, defender)
    assert move.get_power(battle, None, defender) == move.power * (2 if doubled else 1)


def test_bounce_paralysis():
    assert create_move(move_id_of("とびはねる")).effects == [("status", "target", "paralysis", 0.3)]


# ---- あかいいと ----

# メロメロにされると、メロメロにした相手もメロメロになる
def test_destiny_knot_infatuates_source():
    attacker = make("カビゴン", ["メロメロ"])
    holder = make("ハガネール", ["だましうち"], item="あかいいと")
    attacker.gender, holder.gender = "male", "female"
    battle = Battle(attacker, holder)

    battle.use_move(attacker, holder, attacker.moves[0])

    assert holder.current_status.infatuated_by is attacker
    assert attacker.current_status.infatuated_by is holder


# 相手がどんかんなら、相手はメロメロにならない
def test_destiny_knot_blocked_by_oblivious():
    attacker = make("カビゴン", ["メロメロ"], ability="どんかん")
    holder = make("ハガネール", ["だましうち"], item="あかいいと")
    attacker.gender, holder.gender = "male", "female"
    battle = Battle(attacker, holder)

    battle.use_move(attacker, holder, attacker.moves[0])

    assert holder.current_status.infatuated_by is attacker
    assert attacker.current_status.infatuated_by is None


# ---- マジックガード ----

def make_magic_guard(moves=("だましうち",), item=None):
    return make("カビゴン", list(moves), ability="マジックガード", item=item)


# どく・やけど・のろい・あくむ・しめつけ・すなあらしのダメージを受けない
def test_magic_guard_prevents_residual_damage():
    guard = make_magic_guard()
    battle = Battle(guard, make("ハガネール", ["だましうち"]))
    status = guard.current_status
    status.status_condition = "sleep"
    status.has_nightmare = True
    status.is_cursed = True
    status.bound_turns_remaining = 2
    battle.weather = "sandstorm"
    battle.weather_turns_remaining = 3

    battle.apply_end_of_turn_status_damage()
    battle.apply_end_of_turn_weather_damage()
    battle.cure_status(guard)
    status.status_condition = "burn"
    battle.apply_end_of_turn_status_damage()
    status.status_condition = "poison"
    status.toxic_counter = 3
    battle.apply_end_of_turn_status_damage()

    assert damage_taken(guard) == 0
    # もうどくのカウンタは進む
    assert status.toxic_counter == 4


# まきびし・ステルスロックのダメージを受けず、どくびしでもどくにならない（第4世代）
def test_magic_guard_prevents_hazards():
    guard = make_magic_guard()
    battle = Battle(Trainer([make("カビゴン", ["だましうち"]), guard]), Trainer([make("ハガネール", ["だましうち"])]))
    battle.trainer1.stealth_rock = True
    battle.trainer1.spikes = 3
    battle.trainer1.toxic_spikes = 2

    battle.switch_in(battle.trainer1, 1)

    assert damage_taken(guard) == 0
    assert guard.current_status.status_condition is None


# やどりぎのタネでHPを奪われず、相手も回復しない
def test_magic_guard_prevents_leech_seed():
    guard = make_magic_guard()
    seeder = make("ハガネール", ["だましうち"])
    seeder.current_status.current_hp = 1
    battle = Battle(guard, seeder)
    guard.current_status.is_seeded = True

    battle.apply_end_of_turn_leech_seed()

    assert damage_taken(guard) == 0
    assert seeder.current_status.current_hp == 1


# いのちのたま・反動技の反動を受けない（いのちのたまのダメージ1.3倍は残る）
@pytest.mark.parametrize("move_name, item", [("だましうち", "いのちのたま"), ("すてみタックル", None)])
def test_magic_guard_prevents_recoil(monkeypatch, move_name, item):
    monkeypatch.setattr("battlelogic.accuracy.random.randint", lambda a, b: 1)
    guard = make_magic_guard([move_name], item=item)
    defender = make("ハガネール", ["だましうち"])
    battle = Battle(guard, defender)

    result = battle.use_move(guard, defender, guard.moves[0])

    assert result["damage"] > 0
    assert damage_taken(guard) == 0


# わるあがきの反動は、第4世代でも防げない
def test_magic_guard_does_not_prevent_struggle_recoil():
    guard = make_magic_guard()
    defender = make("ハガネール", ["だましうち"])
    battle = Battle(guard, defender)

    battle.use_move(guard, defender, Struggle())

    assert damage_taken(guard) == guard.status.hp // 4


# くろいヘドロのダメージ・ゆうばくのダメージを受けない
def test_magic_guard_prevents_item_and_ability_damage(monkeypatch):
    monkeypatch.setattr("battlelogic.accuracy.random.randint", lambda a, b: 1)
    guard = make_magic_guard(["だましうち"], item="くろいヘドロ")
    aftermath = make("ハガネール", ["だましうち"], ability="ゆうばく")
    aftermath.current_status.current_hp = 1
    battle = Battle(guard, aftermath)

    battle.apply_end_of_turn_items()
    battle.use_move(guard, aftermath, guard.moves[0])

    assert battle.is_fainted(aftermath)
    assert damage_taken(guard) == 0


# 第4世代では、まひで動けなくなることが無い（素早さは下がる）
def test_magic_guard_prevents_full_paralysis(monkeypatch):
    monkeypatch.setattr("battlelogic.battle.random.random", lambda: 0.0)
    guard = make_magic_guard()
    battle = Battle(guard, make("ハガネール", ["だましうち"]))
    speed = battle.get_effective_speed(guard)
    guard.current_status.status_condition = "paralysis"

    assert battle.can_act(guard, guard.moves[0])
    assert battle.get_effective_speed(guard) == int(speed * 0.25)


# こんらんの自傷は攻撃扱いなので受ける
def test_magic_guard_takes_confusion_damage(monkeypatch):
    monkeypatch.setattr("battlelogic.battle.random.random", lambda: 0.0)
    guard = make_magic_guard()
    battle = Battle(guard, make("ハガネール", ["だましうち"]))
    guard.current_status.confusion_turns_remaining = 3

    assert not battle.can_act(guard, guard.moves[0])
    assert damage_taken(guard) > 0


# ---- やるき ----

# ねむり状態にならず、ねむるも失敗する
def test_vital_spirit_prevents_sleep():
    vital = make("カビゴン", ["ねむる"], ability="やるき")
    attacker = make("スターミー", ["さいみんじゅつ"])
    battle = Battle(vital, attacker)

    assert not battle.try_apply_status(vital, "sleep", 1.0, source=attacker)
    vital.current_status.current_hp = 1
    battle.use_move(vital, attacker, vital.moves[0])
    assert vital.current_status.status_condition is None
    assert vital.current_status.current_hp == 1
