"""バトルファクトリー本体（src/factory/）のテスト：ポケモン生成・対戦前ヒント・挑戦の進行。"""
import random

import pytest

from agents.random_agent import RandomAgent
from factory import challenge as challenge_module
from factory import rules
from factory.battle_runner import FactoryBattleResult
from factory.challenge import FactoryChallenge
from factory.generation import (generate_opponent_team, generate_rental_candidates,
                                make_factory_pokemon, round_pool)
from factory.hint import Hint, make_hint, most_common_type
from factory.state import FactoryState
from pokemon import Pokemon
from readpokemondata import load_nejiki_pool, load_pokemon_data, load_type_data


def pokemon_id_of(name):
    return next(i for i, entry in enumerate(load_pokemon_data()) if entry["name"] == name)


def type_id_of(name):
    return next(int(i) for i, type_name in load_type_data().items() if type_name == name)


def spec(name, indivisual_id=0, iv=0):
    return make_factory_pokemon(pokemon_id_of(name), indivisual_id, iv, random.Random(0))


def assert_clauses(team):
    assert len({pokemon.pokemon_id for pokemon in team}) == len(team)
    assert len({pokemon.item_id for pokemon in team}) == len(team)


# ---- FactoryPokemon ----

# 同じ FactoryPokemon から作った Pokemon は、何度作っても同じ個体（性別・特性・実数値）で、HP等は全快
def test_factory_pokemon_build_is_same_individual():
    pokemon = make_factory_pokemon(pokemon_id_of("リザードン"), 2, 16, random.Random(3))
    first, second = pokemon.build(), pokemon.build()
    first.current_status.current_hp = 1
    first.moves[0].current_pp = 0

    assert (second.gender, second.ability.id, second.status) == (first.gender, first.ability.id, first.status)
    assert second.current_status.current_hp == second.status.hp
    assert second.moves[0].current_pp == second.moves[0].pp
    assert (second.level, second.iv) == (rules.OPEN_LEVEL, 16)


def test_factory_pokemon_properties_follow_set_data():
    pokemon = spec("フシギバナ", 0)
    set_data = load_pokemon_data()[pokemon.pokemon_id]["indivisual"][0]
    assert pokemon.name == "フシギバナ"
    assert pokemon.item_id == set_data["item"]
    assert pokemon.move_ids == set_data["move"]
    assert pokemon.types == (type_id_of("くさ"), type_id_of("どく"))


# 種族が持てない特性を指定するのは誤り
def test_pokemon_rejects_ability_the_species_cannot_have():
    entry = load_pokemon_data()[0]
    other = next(ability for e in load_pokemon_data() for ability in e["ability"] if ability not in entry["ability"])
    with pytest.raises(ValueError):
        Pokemon(0, 0, ability_id=other)


# ---- レンタル候補 ----

@pytest.mark.parametrize("seed", range(10))
@pytest.mark.parametrize("round_number", [1, 3, 5, 9])
def test_rental_candidates_without_strong(seed, round_number):
    candidates = generate_rental_candidates(round_number, 0, random.Random(seed))

    assert len(candidates) == rules.RENTAL_CANDIDATE_COUNT
    assert_clauses(candidates)
    pool = set(round_pool(round_number))
    for pokemon in candidates:
        assert (pokemon.pokemon_id, pokemon.indivisual_id) in pool
        assert pokemon.iv == rules.iv_for_round(round_number)
        assert pokemon.level == rules.OPEN_LEVEL


# 3周目開始時に累計14回なら、4周目相当（個体値12）が2体と、3周目相当（個体値8）が4体
@pytest.mark.parametrize("seed", range(10))
def test_rental_candidates_with_strong(seed):
    candidates = generate_rental_candidates(3, 14, random.Random(seed))

    assert_clauses(candidates)
    strong = [pokemon for pokemon in candidates if pokemon.iv == 12]
    normal = [pokemon for pokemon in candidates if pokemon.iv == 8]
    assert (len(strong), len(normal)) == (2, 4)
    assert all((pokemon.pokemon_id, pokemon.indivisual_id) in set(round_pool(4)) for pokemon in strong)
    assert all((pokemon.pokemon_id, pokemon.indivisual_id) in set(round_pool(3)) for pokemon in normal)


# 伝説は5周目以降のプールにしかいない（4周目までのレンタルには出ない）
def test_legendaries_only_from_round_5():
    for round_number in range(1, 5):
        assert not any(load_pokemon_data()[pokemon_id]["legendary"] for pokemon_id, _ in round_pool(round_number))
    assert any(load_pokemon_data()[pokemon_id]["legendary"] for pokemon_id, _ in round_pool(5))


# 1〜4周目のプールは、その周のバリエーションだけ
@pytest.mark.parametrize("round_number", [1, 2, 3, 4])
def test_round_pool_uses_variation_of_round(round_number):
    entries = load_pokemon_data()
    variations = {entries[pokemon_id]["indivisual"][indivisual_id]["variation"]
                  for pokemon_id, indivisual_id in round_pool(round_number)}
    assert variations == {round_number}


# ---- 相手のチーム ----

def player_team_for_test():
    return [spec("リザードン"), spec("カメックス"), spec("フシギバナ")]


# 相手のチームには、プレイヤーと同じ種族・同じ持ち物が出ない
@pytest.mark.parametrize("seed", range(20))
def test_opponent_team_excludes_player_species_and_items(seed):
    player = player_team_for_test()
    team = generate_opponent_team(5, 3, 31, player, random.Random(seed))

    assert len(team) == rules.TEAM_SIZE
    assert_clauses(team)
    assert not {pokemon.pokemon_id for pokemon in team} & {pokemon.pokemon_id for pokemon in player}
    assert not {pokemon.item_id for pokemon in team} & {pokemon.item_id for pokemon in player}


# 第1〜6戦：1周目は1周目だけ、それ以降は今の周か1つ前の周（チーム全員が同じ周）
@pytest.mark.parametrize("seed", range(20))
def test_opponent_team_round_for_battles_1_to_6(seed):
    rng = random.Random(seed)
    team = generate_opponent_team(1, 4, 4, player_team_for_test(), rng)
    assert {pokemon.source_round for pokemon in team} == {1}
    assert {pokemon.iv for pokemon in team} == {0}

    team = generate_opponent_team(3, 2, 16, player_team_for_test(), rng)
    (source_round,) = {pokemon.source_round for pokemon in team}
    assert source_round in (2, 3)
    assert {pokemon.iv for pokemon in team} == {rules.iv_for_round(source_round)}
    assert all((pokemon.pokemon_id, pokemon.indivisual_id) in set(round_pool(source_round)) for pokemon in team)


# 第1〜6戦では、今の周と1つ前の周のどちらも出てくる
def test_opponent_team_uses_both_current_and_previous_round():
    rng = random.Random(0)
    rounds = {generate_opponent_team(4, 1, 22, player_team_for_test(), rng)[0].source_round for _ in range(50)}
    assert rounds == {3, 4}


# 第7戦は次の周の構成・個体値
@pytest.mark.parametrize("round_number", [1, 2, 4, 5, 8])
def test_opponent_team_for_battle_7_uses_next_round(round_number):
    battle_number = (round_number - 1) * 7 + 7
    team = generate_opponent_team(round_number, 7, battle_number, player_team_for_test(), random.Random(0))
    assert {pokemon.iv for pokemon in team} == {rules.iv_for_round(round_number + 1)}
    assert all((pokemon.pokemon_id, pokemon.indivisual_id) in set(round_pool(round_number + 1)) for pokemon in team)


# ネジキ戦：21戦目は銀（バリエーション1・伝説なし・個体値12）、49戦目は金（バリエーション4＋伝説・個体値31）
@pytest.mark.parametrize("seed", range(10))
def test_nejiki_teams(seed):
    rng = random.Random(seed)
    silver = generate_opponent_team(3, 7, 21, player_team_for_test(), rng)
    gold = generate_opponent_team(7, 7, 49, player_team_for_test(), rng)

    assert {pokemon.iv for pokemon in silver} == {12}
    assert {pokemon.source_round for pokemon in silver} == {"silver"}
    assert all((pokemon.pokemon_id, pokemon.indivisual_id) in set(load_nejiki_pool("silver")) for pokemon in silver)
    assert not any(pokemon.is_legendary for pokemon in silver)
    assert {pokemon.iv for pokemon in gold} == {31}
    assert all((pokemon.pokemon_id, pokemon.indivisual_id) in set(load_nejiki_pool("gold")) for pokemon in gold)
    assert_clauses(silver)
    assert_clauses(gold)


# ---- 対戦前ヒント ----

def test_hint_contents_by_round():
    team = [spec("リザードン"), spec("カメックス"), spec("フシギバナ")]
    ids = tuple(pokemon.pokemon_id for pokemon in team)
    first_move = team[0].move_ids[0]

    assert make_hint(1, team) == Hint(rules.HINT_ALL_NAMES, pokemon_ids=ids)
    assert make_hint(2, team) == Hint(rules.HINT_FIRST_TWO_NAMES, pokemon_ids=ids[:2])
    assert make_hint(3, team) == Hint(rules.HINT_LEAD_NAME_AND_MOVE, pokemon_ids=ids[:1], move_id=first_move)
    assert make_hint(4, team) == Hint(rules.HINT_LEAD_MOVE, move_id=first_move)
    assert make_hint(5, team).kind == rules.HINT_MOST_COMMON_TYPE
    assert make_hint(5, team).pokemon_ids is None and make_hint(5, team).move_id is None


# 最も多いタイプ：数が多い方を優先する
def test_most_common_type_by_count():
    # カメックス（みず）・ラプラス（みず/こおり）・リザードン（ほのお/ひこう） → みず2
    team = [spec("リザードン"), spec("カメックス"), spec("ラプラス")]
    assert most_common_type(team) == type_id_of("みず")


# 最も多いタイプ：同数なら第4世代の内部番号が小さい方（ノーマル→かくとう→ひこう→どく→…）
def test_most_common_type_tie_breaks_by_internal_order():
    # リザードン（ほのお/ひこう）・カメックス（みず）・フシギバナ（くさ/どく） → すべて1つずつで、ひこうが最優先
    team = [spec("カメックス"), spec("フシギバナ"), spec("リザードン")]
    assert most_common_type(team) == type_id_of("ひこう")
    # カメックス（みず）・リザードン（ほのお/ひこう）だけなら、ひこう→ほのお→みず の順
    assert most_common_type([spec("カメックス"), spec("リザードン")]) == type_id_of("ひこう")
    # みず と ほのお（data/type.jsonでは ほのお=1・みず=2 だが、内部番号でも ほのお が先）
    assert most_common_type([spec("カメックス"), spec("ブーバーン")]) == type_id_of("ほのお")
    # data/type.jsonのIDの順（ほのお=1・みず=2・かくとう=6・どく=7）ではなく、内部番号の順（かくとう・どく が先）になる
    assert most_common_type([spec("ブーバーン"), spec("カイリキー")]) == type_id_of("かくとう")
    assert most_common_type([spec("カメックス"), spec("ベトベトン")]) == type_id_of("どく")


# ---- 挑戦の進行 ----

# すべての判断を記録し、決まった選び方をする Agent（対戦中はランダム）
class ScriptedAgent(RandomAgent):
    def __init__(self, trade=None):
        super().__init__(random.Random(0))
        self.trade = trade
        self.rental_observations = []
        self.order_observations = []
        self.trade_observations = []

    def choose_rentals(self, observation):
        self.rental_observations.append(observation)
        return [0, 1, 2]

    def choose_order(self, observation):
        self.order_observations.append(observation)
        return [0, 1, 2]

    def choose_trade(self, observation):
        self.trade_observations.append(observation)
        return self.trade


# 対戦の結果を決めておく（outcomesを順に返し、尽きたら勝ち続ける）
def rig_battles(monkeypatch, outcomes=()):
    outcomes = list(outcomes)
    opponents = []

    def fake_battle(player_team, player_agent, opponent_team, context, hint, rng, opponent_agent=None):
        opponents.append((context, list(opponent_team)))
        won = outcomes.pop(0) if outcomes else True
        return FactoryBattleResult(won=won, is_draw=False, timed_out=False, turns=1, battle=None)

    monkeypatch.setattr(challenge_module, "run_factory_battle", fake_battle)
    return opponents


# 7戦ごとにレンタル、第1〜6戦の後に交換、周クリアでBP、21・49戦目でプリント
def test_challenge_progression(monkeypatch):
    opponents = rig_battles(monkeypatch)
    agent = ScriptedAgent()
    challenge = FactoryChallenge(agent, random.Random(0))

    result = challenge.play_challenge(max_battles=56)

    assert result.win_streak == 56 and not result.lost
    assert len(agent.rental_observations) == 8
    assert [observation.context.win_streak for observation in agent.rental_observations] == list(range(0, 56, 7))
    assert len(agent.trade_observations) == 8 * 6
    assert all(observation.context.battle_in_round != 1 for observation in agent.trade_observations)
    assert result.bp_earned == 5 + 5 + 20 + 5 + 7 + 7 + 20 + 9
    assert challenge.state.bp == result.bp_earned
    assert challenge.state.prints == {"silver": True, "gold": True}
    # 交換しないので、累計回数はレンタルの回数だけ
    assert challenge.state.rent_trade_count == 8

    nejiki = [(context.battle_number, team[0].source_round) for context, team in opponents if context.is_nejiki]
    assert nejiki == [(21, "silver"), (49, "gold")]


# 交換すると、自分の1体が直前の相手の1体に入れ替わり、累計回数が増える（強いポケモンの数に効く）
def test_trade_replaces_member_and_counts(monkeypatch):
    opponents = rig_battles(monkeypatch)
    agent = ScriptedAgent(trade=(1, 2))
    challenge = FactoryChallenge(agent, random.Random(0))

    result = challenge.play_challenge(max_battles=8)

    assert result.battles[0].trade == (1, 2)
    first_opponent = opponents[0][1]
    assert result.battles[1].player_team[1] == first_opponent[2]
    # 交換の観測には、相手の種族だけが入る
    assert agent.trade_observations[0].opponent_pokemon_ids == tuple(p.pokemon_id for p in first_opponent)
    # 1周目でレンタル1回＋交換6回＝7回なので、2周目のレンタル候補には強いポケモンが1体
    second_rental = agent.rental_observations[1]
    assert second_rental.context.rent_trade_count == 7
    assert sorted(pokemon.iv for pokemon in second_rental.candidates) == [4] * 5 + [8]


# 負けたら挑戦が終わり、連勝等は0に戻る（BP・プリントは残る）
def test_loss_resets_streak_but_keeps_bp(monkeypatch):
    rig_battles(monkeypatch, outcomes=[True] * 7 + [False])
    challenge = FactoryChallenge(ScriptedAgent(), random.Random(0))

    result = challenge.play_challenge()

    assert result.lost and result.win_streak == 7 and result.rounds_cleared == 1
    assert len(result.battles) == 8
    assert challenge.state.win_streak == 0 and challenge.state.rent_trade_count == 0
    assert challenge.state.player_team == []
    assert challenge.state.bp == 5


# 並び順は Agent が決め、ヒントは並び順を決める前に渡る
def test_order_is_applied_and_hint_is_given(monkeypatch):
    rig_battles(monkeypatch)

    class ReverseAgent(ScriptedAgent):
        def choose_order(self, observation):
            super().choose_order(observation)
            return [2, 1, 0]

    agent = ReverseAgent()
    challenge = FactoryChallenge(agent, random.Random(0))
    challenge.rent()
    rented = list(challenge.state.player_team)
    record = challenge.play_battle()

    assert record.player_team == rented[::-1]
    assert agent.order_observations[0].hint == record.hint
    assert record.hint.kind == rules.HINT_ALL_NAMES
    assert record.hint.pokemon_ids == tuple(pokemon.pokemon_id for pokemon in record.opponent_team)


@pytest.mark.parametrize("method, value", [
    ("choose_rentals", [0, 0, 1]), ("choose_rentals", [0, 1]), ("choose_rentals", [0, 1, 6]),
    ("choose_order", [0, 0, 1]), ("choose_trade", (3, 0)),
])
def test_invalid_decisions_raise(monkeypatch, method, value):
    rig_battles(monkeypatch)
    agent = ScriptedAgent()
    monkeypatch.setattr(agent, method, lambda observation: value)
    with pytest.raises(ValueError):
        FactoryChallenge(agent, random.Random(0)).play_challenge(max_battles=2)


# ---- 実際の対戦を含む挑戦 ----

def play(seed):
    challenge = FactoryChallenge(RandomAgent(random.Random(seed)), random.Random(seed))
    return challenge.play_challenge(max_battles=10)


def summary_of(result):
    return [(record.battle_number, record.won, record.turns, [(p.pokemon_id, p.indivisual_id, p.gender, p.ability_id)
                                                             for p in record.player_team + record.opponent_team])
            for record in result.battles]


# 同じシードなら、同じ挑戦になる
@pytest.mark.parametrize("seed", range(5))
def test_challenge_is_reproducible(seed):
    assert summary_of(play(seed)) == summary_of(play(seed))


def test_different_seeds_give_different_challenges():
    assert len({str(summary_of(play(seed))) for seed in range(5)}) > 1


# 実際に対戦し、勝てば次の対戦に進み、負けたら終わる
@pytest.mark.parametrize("seed", range(5))
def test_real_challenge_runs(seed):
    result = play(seed)
    assert all(record.won for record in result.battles[:-1])
    assert result.lost == (not result.battles[-1].won)
    assert result.win_streak == sum(record.won for record in result.battles)


def test_state_defaults():
    state = FactoryState()
    assert (state.round_number, state.battle_in_round, state.battle_number) == (1, 1, 1)
    assert state.prints == {"silver": False, "gold": False}
