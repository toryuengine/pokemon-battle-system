"""対戦エンジンに Agent を繋ぐための口（乱数の差し替え・技選択と交代先のポリシー・引き分けの扱い・イベントの記録）のテスト。"""
import random

import pytest

from ability.base_ability import NO_ABILITY
from battlelogic.battle import Battle
from move.movefactory import create_move
from pokemon import Pokemon
from readpokemondata import load_move_data, load_pokemon_data
from trainer import Trainer


def pokemon_id_of(name):
    return next(i for i, entry in enumerate(load_pokemon_data()) if entry["name"] == name)


def move_id_of(name):
    return next(int(i) for i, data in load_move_data().items() if data["name"] == name)


# 種族名・技名のリストからポケモンを作る（特性なし・持ち物なし）
def make(name, moves, level=50):
    pokemon = Pokemon(pokemon_id_of(name), 0, level=level, iv=31, rng=random.Random(0))
    pokemon.moves = [create_move(move_id_of(move_name)) for move_name in moves]
    pokemon.ability = NO_ABILITY
    pokemon.item = None
    return pokemon


# seedから3体ずつの手持ちを作り、同じseedの乱数で対戦させる
def run_seeded_battle(seed):
    rng = random.Random(seed)
    pokemon_count = len(load_pokemon_data())
    parties = [[Pokemon(rng.randrange(pokemon_count), rng.randrange(4), rng=rng) for _ in range(3)] for _ in range(2)]
    battle = Battle(Trainer(parties[0]), Trainer(parties[1]), rng=rng)
    battle.start_battle()
    return battle


def event_tuples(battle):
    return [(event.turn, event.kind, event.side, sorted(event.data.items())) for event in battle.events]


# ---- 乱数 ----

# 同じシードなら、経過（イベント）まで含めて全く同じ対戦になる
@pytest.mark.parametrize("seed", range(20))
def test_same_seed_reproduces_battle(seed):
    first = run_seeded_battle(seed)
    second = run_seeded_battle(seed)

    assert event_tuples(first) == event_tuples(second)
    assert first.turn == second.turn


# シードが違えば、違う対戦になる（乱数が本当に差し替わっている）
def test_different_seeds_give_different_battles():
    results = {tuple(map(str, event_tuples(run_seeded_battle(seed)))) for seed in range(10)}
    assert len(results) > 1


# ---- 技選択のポリシー ----

# move_policyには選べる技だけが渡され、選んだ技がそのまま使われる
def test_move_policy_chooses_move():
    seen = []

    def policy(battle, trainer, moves):
        seen.append([move.id for move in moves])
        return next(move for move in moves if move.id == move_id_of("てっぺき"))

    user = make("カビゴン", ["だましうち", "てっぺき"])
    battle = Battle(Trainer([user], move_policy=policy), make("ハピナス", ["てっぺき"]), rng=random.Random(0))
    battle.MAX_TURNS = 3
    battle.start_battle()

    assert seen and all(sorted(ids) == sorted([move_id_of("だましうち"), move_id_of("てっぺき")]) for ids in seen)
    used = [event.data["move_id"] for event in battle.events if event.kind == "move" and event.side == 1]
    assert used == [move_id_of("てっぺき")] * 3


# ちょうはつ等で選べない技は、move_policyに渡されない
def test_move_policy_receives_only_selectable_moves():
    seen = []

    def policy(battle, trainer, moves):
        seen.append([move.id for move in moves])
        return moves[0]

    user = make("カビゴン", ["だましうち", "てっぺき"])
    battle = Battle(Trainer([user], move_policy=policy), make("ハピナス", ["てっぺき"]), rng=random.Random(0))
    user.current_status.taunt_turns_remaining = 3

    battle.select_move(user)

    assert seen == [[move_id_of("だましうち")]]


# 選べない技を返すポリシーは誤り
def test_move_policy_invalid_choice_raises():
    user = make("カビゴン", ["だましうち"])
    battle = Battle(Trainer([user], move_policy=lambda battle, trainer, moves: create_move(move_id_of("だましうち"))),
                    make("ハピナス", ["てっぺき"]))

    with pytest.raises(ValueError):
        battle.select_move(user)


# ---- 交代先のポリシー ----

# 瀕死の交代先はreplacement_policyで選ぶ
def test_replacement_policy_on_faint():
    calls = []

    def policy(battle, trainer, candidates, reason):
        calls.append((candidates, reason))
        return candidates[-1]

    party = [make("カビゴン", ["だましうち"]), make("ハピナス", ["だましうち"]), make("ハガネール", ["だましうち"])]
    battle = Battle(Trainer(party, replacement_policy=policy), make("ハピナス", ["てっぺき"]))
    party[0].current_status.current_hp = 0

    battle.resolve_faints()

    assert calls == [([1, 2], "faint")]
    assert battle.pokemon1 is party[2]
    switch_events = [event for event in battle.events if event.kind == "switch_in"]
    assert switch_events[-1].side == 1 and switch_events[-1].data["party_index"] == 2
    assert switch_events[-1].data["reason"] == "faint"


# 両者が同時に瀕死になったら、相手の交代先を見ないまま両者が選ぶ
def test_simultaneous_faint_choices_do_not_see_each_other():
    seen_opponent = []

    def policy2(battle, trainer, candidates, reason):
        seen_opponent.append(battle.trainer1.active_index)
        return candidates[0]

    party1 = [make("カビゴン", ["だましうち"]), make("ハピナス", ["だましうち"])]
    party2 = [make("カビゴン", ["だましうち"]), make("ハピナス", ["だましうち"])]
    battle = Battle(Trainer(party1), Trainer(party2, replacement_policy=policy2))
    party1[0].current_status.current_hp = 0
    party2[0].current_status.current_hp = 0

    battle.resolve_faints()

    assert seen_opponent == [0]
    assert battle.pokemon1 is party1[1] and battle.pokemon2 is party2[1]


# とんぼがえり・バトンタッチの交代先もreplacement_policyで選ぶ
@pytest.mark.parametrize("move_name, reason", [("とんぼがえり", "u_turn"), ("バトンタッチ", "baton_pass")])
def test_replacement_policy_on_self_switch(move_name, reason):
    calls = []

    def policy(battle, trainer, candidates, reason):
        calls.append(reason)
        return candidates[-1]

    party = [make("ハッサム", [move_name]), make("ハピナス", ["てっぺき"]), make("ハガネール", ["てっぺき"])]
    battle = Battle(Trainer(party, replacement_policy=policy), make("カビゴン", ["てっぺき"]), rng=random.Random(0))
    battle.MAX_TURNS = 1
    battle.start_battle()

    assert calls == [reason]
    assert battle.pokemon1 is party[2]


# 交代先に選べない個体を返すポリシーは誤り
def test_replacement_policy_invalid_choice_raises():
    party = [make("カビゴン", ["だましうち"]), make("ハピナス", ["だましうち"])]
    battle = Battle(Trainer(party, replacement_policy=lambda battle, trainer, candidates, reason: 0),
                    make("ハピナス", ["てっぺき"]))
    party[0].current_status.current_hp = 0

    with pytest.raises(ValueError):
        battle.resolve_faints()


# ---- 引き分け ----

# 同時全滅はdraw_winnerに渡したトレーナーの勝ち（ファクトリーでは相手を渡してプレイヤーの負けにする）
def test_draw_winner():
    trainer1 = Trainer([make("カビゴン", ["だましうち"])])
    trainer2 = Trainer([make("ハピナス", ["だましうち"])])
    battle = Battle(trainer1, trainer2)
    trainer1.active.current_status.current_hp = 0
    trainer2.active.current_status.current_hp = 0

    assert battle.get_winning_trainer() is None
    assert battle.get_winning_trainer(draw_winner=trainer2) is trainer2


def test_winning_trainer():
    trainer1 = Trainer([make("カビゴン", ["だましうち"])])
    trainer2 = Trainer([make("ハピナス", ["だましうち"])])
    battle = Battle(trainer1, trainer2)
    assert battle.get_winning_trainer() is None

    trainer2.active.current_status.current_hp = 0
    assert battle.get_winning_trainer(draw_winner=trainer2) is trainer1


# ---- イベント ----

# 対戦の経過は先発の登場で始まり、battle_endで終わる。HPの変化は途切れずに繋がり、瀕死の数も合う
@pytest.mark.parametrize("seed", range(20))
def test_events_are_consistent(seed):
    battle = run_seeded_battle(seed)
    events = battle.events

    assert [(event.kind, event.side, event.data["reason"]) for event in events[:2]] == [
        ("switch_in", 1, "lead"), ("switch_in", 2, "lead")]
    assert events[-1].kind == "battle_end"
    winner = battle.get_winning_trainer()
    assert events[-1].data["winner_side"] == (None if winner is None else battle.get_side(winner))

    hp = {}
    for side, trainer in ((1, battle.trainer1), (2, battle.trainer2)):
        for index, pokemon in enumerate(trainer.party):
            hp[(side, index)] = pokemon.status.hp
    for event in events:
        if event.kind == "hp":
            key = (event.side, event.data["party_index"])
            assert event.data["before"] == hp[key]
            hp[key] = event.data["after"]
    for side, trainer in ((1, battle.trainer1), (2, battle.trainer2)):
        for index, pokemon in enumerate(trainer.party):
            assert hp[(side, index)] == pokemon.current_status.current_hp

    faint_count = sum(1 for event in events if event.kind == "faint")
    fainted = sum(1 for trainer in (battle.trainer1, battle.trainer2) for pokemon in trainer.party
                  if pokemon.current_status.current_hp == 0)
    assert faint_count == fainted


# 技を出すたびにmoveとmove_resultが対になって記録される
def test_move_events_are_paired():
    battle = run_seeded_battle(0)
    kinds = [event.kind for event in battle.events if event.kind in ("move", "move_result")]
    assert kinds == ["move", "move_result"] * (len(kinds) // 2)


# record_events=Falseなら何も記録しない
def test_record_events_disabled():
    battle = Battle(make("カビゴン", ["だましうち"]), make("ハピナス", ["だましうち"]), record_events=False)
    battle.MAX_TURNS = 2
    battle.start_battle()
    assert battle.events == []
