"""状態異常を防ぐ特性（めんえき・ふみん・やるき・マイペース・みずのベール・どんかん）が、
すでにかかっている状態異常を治すことのテスト（BaseAbility.on_update）。"""
import random

import pytest

from ability.abilityfactory import create_ability
from ability.base_ability import NO_ABILITY
from battlelogic.battle import Battle
from item.itemfactory import create_item
from move.movefactory import create_move
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


def make(name, moves, ability=None, item=None):
    pokemon = Pokemon(pokemon_id_of(name), 0, level=50, iv=31, rng=random.Random(0))
    pokemon.moves = [create_move(move_id_of(move_name)) for move_name in moves]
    if ability is not None:
        pokemon.ability = create_ability(ability_id_of(ability))
        pokemon.original_ability_id = pokemon.ability.id
    else:
        pokemon.ability = NO_ABILITY
    pokemon.item = create_item(item_id_of(item)) if item is not None else None
    return pokemon


def ability_reveals(battle):
    return [(event.side, event.data["ability_id"]) for event in battle.events if event.kind == "ability"]


# かかっている状態異常を、その状態異常を防ぐ特性にしたときの状態をまとめて作る
def afflict(pokemon, condition):
    status = pokemon.current_status
    if condition == "confusion":
        status.confusion_turns_remaining = 3
    else:
        status.status_condition = condition
        if condition == "sleep":
            status.sleep_turns_remaining = 3


def is_afflicted(pokemon, condition):
    status = pokemon.current_status
    if condition == "confusion":
        return status.confusion_turns_remaining > 0
    return status.status_condition == condition


@pytest.mark.parametrize("ability, condition", [
    ("めんえき", "poison"),
    ("ふみん", "sleep"),
    ("やるき", "sleep"),
    ("マイペース", "confusion"),
    ("みずのベール", "burn"),
])
def test_immunity_ability_cures_existing_status(ability, condition):
    pokemon = make("カビゴン", ["だましうち"], ability=ability)
    battle = Battle(pokemon, make("ハガネール", ["だましうち"]), rng=random.Random(0))
    afflict(pokemon, condition)

    battle.activate_held_items_on_field()

    assert not is_afflicted(pokemon, condition)
    assert ability_reveals(battle) == [(1, ability_id_of(ability))]


# 防ぐ状態異常と違う状態異常は治さない
def test_immunity_ability_does_not_cure_other_status():
    pokemon = make("カビゴン", ["だましうち"], ability="めんえき")
    battle = Battle(pokemon, make("ハガネール", ["だましうち"]), rng=random.Random(0))
    afflict(pokemon, "paralysis")

    battle.activate_held_items_on_field()

    assert pokemon.current_status.status_condition == "paralysis"
    assert ability_reveals(battle) == []


# もうどくも、めんえきで治る（ダメージのカウンタも戻る）
def test_immunity_cures_toxic():
    pokemon = make("カビゴン", ["だましうち"], ability="めんえき")
    battle = Battle(pokemon, make("ハガネール", ["だましうち"]), rng=random.Random(0))
    battle.inflict_poison(pokemon, badly=True)

    battle.activate_held_items_on_field()

    assert pokemon.current_status.status_condition is None
    assert pokemon.current_status.toxic_counter == 0


def test_oblivious_cures_infatuation():
    attacker = make("カビゴン", ["だましうち"])
    pokemon = make("ハガネール", ["だましうち"], ability="どんかん")
    battle = Battle(attacker, pokemon, rng=random.Random(0))
    pokemon.current_status.infatuated_by = attacker

    battle.activate_held_items_on_field()

    assert pokemon.current_status.infatuated_by is None
    assert ability_reveals(battle) == [(2, ability_id_of("どんかん"))]


# いえきで特性を消されている間は治らない
def test_suppressed_ability_does_not_cure():
    pokemon = make("カビゴン", ["だましうち"], ability="めんえき")
    battle = Battle(pokemon, make("ハガネール", ["だましうち"]), rng=random.Random(0))
    afflict(pokemon, "poison")
    pokemon.current_status.is_ability_suppressed = True

    battle.activate_held_items_on_field()

    assert pokemon.current_status.status_condition == "poison"


# どくの個体がトレースでめんえきをコピーすると、場に出た直後にどくが治る
def test_trace_into_immunity_cures_poison():
    lead = make("カビゴン", ["だましうち"])
    tracer = make("ポリゴン2", ["だましうち"], ability="トレース")
    afflict(tracer, "poison")
    opponent = make("ハガネール", ["だましうち"], ability="めんえき")
    battle = Battle(Trainer([lead, tracer]), opponent, rng=random.Random(0))

    battle.switch_in(battle.trainer1, 1)

    assert tracer.ability.id == ability_id_of("めんえき")
    assert tracer.current_status.status_condition is None


# ものまね（へんしん）でふみんをコピーすると、行動の後にねむりが治る
def test_transform_into_insomnia_cures_sleep(monkeypatch):
    transformer = make("カビゴン", ["ものまね"])
    target = make("ハガネール", ["だましうち"], ability="ふみん")
    battle = Battle(transformer, target, rng=random.Random(0))
    afflict(transformer, "sleep")
    # ねむっていても行動できたことにして、へんしんの後の処理だけを確かめる
    monkeypatch.setattr(battle, "can_act", lambda pokemon, move: True)

    battle.execute_move_action(transformer, transformer.moves[0])

    assert transformer.ability.id == ability_id_of("ふみん")
    assert transformer.current_status.status_condition is None


# かたやぶりの相手のどくどくでどくになっても、技の後すぐにめんえきで治る
def test_mold_breaker_poison_is_cured_after_move(monkeypatch):
    attacker = make("カビゴン", ["どくどく"], ability="かたやぶり")
    pokemon = make("カビゴン", ["だましうち"], ability="めんえき")
    battle = Battle(attacker, pokemon, rng=random.Random(0))
    poisoned = []
    original_try_apply_status = battle.try_apply_status

    def spy(target, condition, chance, **kwargs):
        result = original_try_apply_status(target, condition, chance, **kwargs)
        poisoned.append(result)
        return result

    monkeypatch.setattr(battle, "try_apply_status", spy)
    monkeypatch.setattr(battle, "can_act", lambda pokemon, move: True)

    battle.execute_move_action(attacker, attacker.moves[0])

    assert poisoned == [True]
    assert pokemon.current_status.status_condition is None


# 特性が持ち物より先に治すので、めんえきで治るどくにラムのみは使わない
def test_ability_cures_before_berry():
    pokemon = make("カビゴン", ["だましうち"], ability="めんえき", item="ラムのみ")
    battle = Battle(pokemon, make("ハガネール", ["だましうち"]), rng=random.Random(0))
    afflict(pokemon, "poison")

    battle.activate_held_items_on_field()

    assert pokemon.current_status.status_condition is None
    assert pokemon.item is not None
