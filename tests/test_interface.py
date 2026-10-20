"""ユーザーが触る部分（src/interface/）と、そのために足した観測（見える出来事）・進行（play_next）のテスト。"""
import random

import pytest

from agents.random_agent import RandomAgent
from factory.battle_runner import run_factory_battle, to_visible_event
from factory.challenge import FactoryChallenge
from factory.generation import make_factory_pokemon
from factory.observation import OWNER_OPPONENT, OWNER_OWN, FactoryContext
from interface import cli
from interface.human_agent import HumanAgent, QuitGame
from interface.narrator import Narrator
from interface.spectator import SpectatorAgent
from readpokemondata import load_pokemon_data

CONTEXT = FactoryContext(round_number=1, battle_in_round=1, win_streak=0, battle_number=1, rent_trade_count=1,
                         is_nejiki=False)


def random_team(rng):
    ids = rng.sample(range(len(load_pokemon_data())), 3)
    return [make_factory_pokemon(pokemon_id, rng.randrange(4), 31, rng) for pokemon_id in ids]


# 見える出来事を全部集める Agent（判断はランダム）
class RecordingAgent(RandomAgent):
    def __init__(self, rng):
        super().__init__(rng)
        self.events = []
        self.end = None

    def choose_action(self, observation):
        self.events.extend(observation.new_events)
        return super().choose_action(observation)

    def choose_replacement(self, observation, reason):
        self.events.extend(observation.new_events)
        return super().choose_replacement(observation, reason)

    def on_battle_end(self, observation):
        self.events.extend(observation.new_events)
        self.end = observation


# ---- 見える出来事 ----

# 観測の new_events を順に繋ぐと、対戦の経過を漏れも重なりもなく見える形にしたものになり、最後は決着で終わる
@pytest.mark.parametrize("seed", range(10))
def test_new_events_cover_whole_battle_once(seed):
    rng = random.Random(seed)
    player_team, opponent_team = random_team(rng), random_team(rng)
    agent = RecordingAgent(random.Random(seed))
    result = run_factory_battle(player_team, agent, opponent_team, CONTEXT, None, rng)

    assert agent.events == [to_visible_event(event, 1) for event in result.battle.events]
    assert agent.events[-1].kind == "battle_end"
    assert agent.events[-1].data["won"] == result.won
    assert (agent.end.won, agent.end.turns) == (result.won, result.turns)


# 相手のセットの番号・相手に与えたダメージの実数・相手の実HPは、見える出来事に入らない
@pytest.mark.parametrize("seed", range(10))
def test_visible_events_hide_opponent_details(seed):
    rng = random.Random(seed)
    agent = RecordingAgent(random.Random(seed))
    run_factory_battle(random_team(rng), agent, random_team(rng), CONTEXT, None, rng)

    for event in agent.events:
        assert "indivisual_id" not in event.data
        assert "damage" not in event.data
        if event.kind == "hp" and event.owner == OWNER_OPPONENT:
            assert set(event.data) == {"before_ratio", "after_ratio"}
        if event.kind == "hp" and event.owner == OWNER_OWN:
            assert {"before", "after", "max_hp"} <= set(event.data)


# 相手にも Agent を付けたときは、相手の Agent にも相手から見た勝敗で知らせる
def test_battle_end_is_told_to_both_sides():
    rng = random.Random(0)
    player, opponent = RecordingAgent(random.Random(1)), RecordingAgent(random.Random(2))
    result = run_factory_battle(random_team(rng), player, random_team(rng), CONTEXT, None, rng,
                                opponent_agent=opponent)
    assert player.end.won == result.won
    assert opponent.end.won == (not result.won)


# ---- 進行（play_next） ----

# play_next で1戦ずつ進めても、play_challenge と同じ挑戦になる
@pytest.mark.parametrize("seed", range(3))
def test_play_next_matches_play_challenge(seed):
    whole = FactoryChallenge(RandomAgent(random.Random(seed)), random.Random(seed)).play_challenge()

    challenge = FactoryChallenge(RandomAgent(random.Random(seed)), random.Random(seed))
    records = []
    while not records or records[-1].won:
        records.append(challenge.play_next())

    assert [(r.battle_number, r.won, r.turns, r.trade) for r in records] == \
        [(r.battle_number, r.won, r.turns, r.trade) for r in whole.battles]
    # 負けたら連勝が0に戻る
    assert challenge.state.win_streak == 0


# on_battle_end は交換を聞く前に、更新後の連勝で呼ばれる
def test_play_next_calls_on_battle_end_before_trade():
    calls = []

    class Agent(RandomAgent):
        def choose_trade(self, observation):
            calls.append("trade")
            return None

    challenge = FactoryChallenge(Agent(random.Random(0)), random.Random(0))
    record = challenge.play_next(on_battle_end=lambda r: calls.append(("end", challenge.state.win_streak)))
    if record.won:
        assert calls == [("end", 1), "trade"]
    else:
        assert calls == [("end", 0)]


# ---- 人間用の Agent ----

# 決まった入力を流し込む。prompt の中身で何を答えるかを決める
def scripted_input(answers=None, rentals="1 2 3", order="", action="1", trade="", again="n"):
    log = []
    queue = list(answers or [])

    def input_fn(prompt):
        log.append(prompt)
        if queue:
            return queue.pop(0)
        if "借りる" in prompt:
            return rentals
        if "並び順" in prompt:
            return order
        if "交換" in prompt:
            return trade
        if "もう一度" in prompt:
            return again
        return action
    return input_fn, log


# いつも最初の選択肢を選ぶ人間で、負けるまで遊べる（表示の途中で例外が起きない）
@pytest.mark.parametrize("seed", range(5))
def test_human_can_play_until_loss(seed):
    input_fn, prompts = scripted_input()
    output = []
    cli.play(seed, None, input_fn=input_fn, output_fn=output.append)

    text = "\n".join(output)
    assert f"seed={seed}" in text
    assert "負け】" in text
    assert any("行動を選んでください" in prompt for prompt in prompts)
    assert prompts[-1].startswith("もう一度")


# 同じシード・同じ入力なら、同じ挑戦になる
def test_human_play_is_reproducible():
    outputs = []
    for _ in range(2):
        input_fn, _ = scripted_input()
        output = []
        cli.play(7, None, input_fn=input_fn, output_fn=output.append)
        outputs.append(output)
    assert outputs[0] == outputs[1]


# 間違った入力は、正しい入力が来るまで聞き直す
def test_human_retries_invalid_input():
    input_fn, prompts = scripted_input(answers=["1 1 2", "7 1 2", "abc", "2 4 6"])
    agent = HumanAgent(input_fn, lambda line: None)
    challenge = FactoryChallenge(agent, random.Random(0))
    challenge.rent()

    assert sum("借りる" in prompt for prompt in prompts) == 4
    candidates_seen = challenge.state.player_team
    assert len(candidates_seen) == 3


def test_human_order_and_trade_parsing():
    input_fn, _ = scripted_input(order="3 1 2", trade="2 1")
    agent = HumanAgent(input_fn, lambda line: None)
    challenge = FactoryChallenge(agent, random.Random(1))
    challenge.rent()
    team = list(challenge.state.player_team)
    record = challenge.play_battle()

    assert record.player_team == [team[2], team[0], team[1]]
    assert challenge.offer_trade() == (1, 0)


# q で途中でやめられる
def test_human_can_quit():
    input_fn, _ = scripted_input(answers=["1 2 3", "q"])
    output = []
    cli.play(0, None, input_fn=input_fn, output_fn=output.append)
    assert output[-1].startswith("やめました")
    with pytest.raises(QuitGame):
        HumanAgent(lambda prompt: "q", lambda line: None).choose_rentals(_rental_observation())


def _rental_observation():
    from factory.generation import generate_rental_candidates
    from factory.observation import RentalObservation
    return RentalObservation(CONTEXT, tuple(generate_rental_candidates(1, 0, random.Random(0))))


# 助言の Agent を付けると、判断のたびにその選択が表示される（実際の選択は人間の入力のまま）
def test_advisor_is_shown():
    input_fn, _ = scripted_input(rentals="4 5 6")
    output = []
    agent = HumanAgent(input_fn, output.append, advisor=RandomAgent(random.Random(0)), advisor_name="random")
    chosen = agent.choose_rentals(_rental_observation())

    assert chosen == [3, 4, 5]
    assert any(line.startswith("  助言（random）: ") for line in output)


# ---- 観戦 ----

# 表示しながら進めても、表示しない自動プレイと同じ挑戦になる（判断も乱数の進み方も変えない）
@pytest.mark.parametrize("seed", range(3))
def test_spectator_does_not_change_challenge(seed):
    plain = FactoryChallenge(RandomAgent(random.Random(seed)), random.Random(seed)).play_challenge()
    output = []
    spectator = SpectatorAgent(RandomAgent(random.Random(seed)), output.append)
    watched = FactoryChallenge(spectator, random.Random(seed)).play_challenge()

    assert [(r.won, r.turns, r.trade) for r in watched.battles] == [(r.won, r.turns, r.trade) for r in plain.battles]
    assert any(line.startswith("  → ") for line in output)


def test_watch_command_runs():
    output = []
    cli.watch("random", 0, 2, False, output_fn=output.append)
    assert output[0] == "観戦: agent=random seed=0"
    assert any(line.startswith("【1戦目") for line in output)


# ---- メッセージ ----

# どの出来事も、例外なくメッセージにできる（名前が引けない個体は出てこない）
@pytest.mark.parametrize("seed", range(10))
def test_narrator_handles_all_events(seed):
    rng = random.Random(seed)
    agent = RecordingAgent(random.Random(seed))
    run_factory_battle(random_team(rng), agent, random_team(rng), CONTEXT, None, rng)
    lines = Narrator().narrate(agent.events)

    assert lines[0].startswith("ゆけっ！")
    assert not any("？" in line for line in lines)
