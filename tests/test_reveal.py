"""特性・持ち物が発動して判明したこと（Battle.eventsの"ability"・"item_activate"）と、それを観測に反映するテスト。"""
import random

from ability.abilityfactory import create_ability
from ability.base_ability import NO_ABILITY
from battlelogic.battle import Battle
from factory.battle_runner import OpponentKnowledge
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


# 種族名・技名のリストからポケモンを作る。特性を指定すれば、それを元の特性にする（指定しなければ「特性なし」）
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


def reveals(battle, kind):
    return [(event.side, event.data) for event in battle.events if event.kind == kind]


def ability_reveals(battle):
    return [(side, data["ability_id"], data["is_original"]) for side, data in reveals(battle, "ability")]


def item_reveals(battle):
    return [(side, data["item_id"]) for side, data in reveals(battle, "item_activate")]


# ---- 特性 ----

# いかくは場に出た時に判明する。相手のクリアボディで防がれたら、クリアボディも判明する
def test_intimidate_and_clear_body_are_revealed():
    intimidator = make("カビゴン", ["だましうち"], ability="いかく")
    clear_body = make("ハガネール", ["だましうち"], ability="クリアボディ")
    battle = Battle(intimidator, clear_body, rng=random.Random(0))

    battle.activate_switch_in_abilities([intimidator, clear_body])

    assert ability_reveals(battle) == [(1, ability_id_of("いかく"), True), (2, ability_id_of("クリアボディ"), True)]
    assert battle.stages2.atk == 0


# プレッシャー・かたやぶりは場に出た時にメッセージが出る
def test_pressure_is_revealed_on_switch_in():
    pressure = make("カビゴン", ["だましうち"], ability="プレッシャー")
    battle = Battle(pressure, make("ハガネール", ["だましうち"]), rng=random.Random(0))

    battle.activate_switch_in_abilities([battle.pokemon1, battle.pokemon2])

    assert ability_reveals(battle) == [(1, ability_id_of("プレッシャー"), True)]


# ちくでんは、でんき技を受けて無効化したときに判明する
def test_volt_absorb_is_revealed_when_absorbing():
    attacker = make("カビゴン", ["10まんボルト"])
    absorber = make("ハガネール", ["だましうち"], ability="ちくでん")
    battle = Battle(attacker, absorber, rng=random.Random(0))

    result = battle.use_move(attacker, absorber, attacker.moves[0])

    assert result.get("blocked_by_ability")
    assert ability_reveals(battle) == [(2, ability_id_of("ちくでん"), True)]


# ふみんは、ねむらせる技を防いだときに判明する
def test_insomnia_is_revealed_when_blocking_sleep_move():
    attacker = make("カビゴン", ["キノコのほうし"])
    insomniac = make("ハガネール", ["だましうち"], ability="ふみん")
    battle = Battle(attacker, insomniac, rng=random.Random(0))

    battle.use_move(attacker, insomniac, attacker.moves[0])

    assert insomniac.current_status.status_condition is None
    assert ability_reveals(battle) == [(2, ability_id_of("ふみん"), True)]


# 追加効果を確率で防いだだけでは何も表示されないので、特性は判明しない
def test_ability_blocking_secondary_effect_is_not_revealed():
    attacker = make("カビゴン", ["だましうち"])
    insomniac = make("ハガネール", ["だましうち"], ability="ふみん")
    battle = Battle(attacker, insomniac, rng=random.Random(0))

    assert not battle.try_apply_status(insomniac, "sleep", 0.3, source=attacker)

    assert ability_reveals(battle) == []


# 倍率が掛かるだけでメッセージの出ない特性（テクニシャン等）は判明しない
def test_silent_ability_is_not_revealed():
    attacker = make("カビゴン", ["だましうち"], ability="テクニシャン")
    defender = make("ハガネール", ["だましうち"])
    battle = Battle(attacker, defender, rng=random.Random(0))

    battle.use_move(attacker, defender, attacker.moves[0])

    assert ability_reveals(battle) == []


# トレースは、トレースと相手の特性の両方が判明する。コピーした特性が発動しても、元の特性としては数えない
def test_trace_reveals_both_abilities():
    tracer = make("カビゴン", ["だましうち"], ability="トレース")
    intimidator = make("ハガネール", ["だましうち"], ability="いかく")
    battle = Battle(tracer, intimidator, rng=random.Random(0))

    battle.activate_switch_in_abilities([tracer])

    assert ability_reveals(battle) == [
        (1, ability_id_of("トレース"), True),
        (2, ability_id_of("いかく"), True),
        (1, ability_id_of("いかく"), False),
    ]
    knowledge = OpponentKnowledge(1)
    battle.record_switch_in(battle.trainer1, "lead")
    knowledge.update(battle)
    assert knowledge.records[0].revealed_ability_id == ability_id_of("トレース")


# ---- 持ち物 ----

# たべのこしは、HPが減っていて回復したときに判明する（HPが満タンなら回復せず、メッセージも出ない）
def test_leftovers_is_revealed_only_when_healing():
    holder = make("カビゴン", ["だましうち"], item="たべのこし")
    battle = Battle(holder, make("ハガネール", ["だましうち"]), rng=random.Random(0))

    battle.apply_end_of_turn_items()
    assert item_reveals(battle) == []

    holder.current_status.current_hp -= 50
    battle.apply_end_of_turn_items()
    assert item_reveals(battle) == [(1, item_id_of("たべのこし"))]


# いのちのたまは、攻撃後にHPが減ったときに判明する
def test_life_orb_is_revealed_by_recoil():
    attacker = make("カビゴン", ["だましうち"], item="いのちのたま")
    defender = make("ハガネール", ["だましうち"])
    battle = Battle(attacker, defender, rng=random.Random(0))

    battle.use_move(attacker, defender, attacker.moves[0])

    assert item_reveals(battle) == [(1, item_id_of("いのちのたま"))]


# ---- 観測への反映 ----

def _knowledge_after(battle, side):
    knowledge = OpponentKnowledge(side)
    knowledge.update(battle)
    return knowledge


# 消費されずに発動した持ち物も、元の持ち物として観測に入る
def test_item_activation_reveals_original_item():
    holder = make("カビゴン", ["だましうち"], item="たべのこし")
    battle = Battle(make("ハガネール", ["だましうち"]), Trainer([holder]), rng=random.Random(0))
    battle.record_switch_in(battle.trainer2, "lead")
    holder.current_status.current_hp -= 50

    battle.apply_end_of_turn_items()

    assert _knowledge_after(battle, 2).records[0].revealed_item_id == item_id_of("たべのこし")


# トリックで受け取った持ち物が発動しても、元の持ち物とは数えない（渡す前の持ち物も分からないまま）
def test_item_activation_after_trick_is_not_original():
    tricker = make("カビゴン", ["トリック"], item="たべのこし")
    receiver = make("ハガネール", ["だましうち"])
    battle = Battle(tricker, receiver, rng=random.Random(0))
    battle.record_switch_in(battle.trainer2, "lead")

    battle.perform_trick(tricker, receiver)
    battle.record_state_changes()
    receiver.current_status.current_hp -= 50
    battle.apply_end_of_turn_items()

    assert item_reveals(battle) == [(2, item_id_of("たべのこし"))]
    assert _knowledge_after(battle, 2).records[0].revealed_item_id is None


# record_events=Falseなら、判明したことも記録しない
def test_reveal_is_not_recorded_without_events():
    intimidator = make("カビゴン", ["だましうち"], ability="いかく")
    battle = Battle(intimidator, make("ハガネール", ["だましうち"]), rng=random.Random(0), record_events=False)

    battle.activate_switch_in_abilities([intimidator])

    assert battle.events == []
    assert battle.stages2.atk == -1
