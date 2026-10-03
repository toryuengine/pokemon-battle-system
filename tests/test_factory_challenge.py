import random

import pytest

from agents.random_agent import RandomAgent
from battlelogic.battle import Battle
from factory import challenge as challenge_module
from factory import rules
from factory.battle_runner import BattleResult, run_battle
from factory.challenge import FactoryChallenge
from factory.observation import FactoryContext, TurnObservation
from pokemon import Pokemon
from trainer import Trainer


def always_win(monkeypatch):
    monkeypatch.setattr(challenge_module, "run_battle", lambda *args, **kwargs: BattleResult(won=True, turns=1))


# 49連勝までの流れ: BP・プリント・ネジキ戦にヒントが無いこと・周ごとにレンタルし直すこと
def test_full_flow_to_gold_print(monkeypatch):
    always_win(monkeypatch)
    challenge = FactoryChallenge(rules.LEVEL_50, RandomAgent(random.Random(0)), random.Random(0))
    result = challenge.run(max_battles=49)

    assert result.win_streak == 49
    assert result.rounds_cleared == 7
    assert result.bp == 5 + 5 + 20 + 5 + 7 + 7 + 20
    assert result.prints == {rules.SILVER: True, rules.GOLD: True}
    brain_records = [r for r in result.battles if r.is_brain_battle]
    assert [r.battle_number for r in brain_records] == [21, 49]
    assert all(r.hint is None for r in brain_records)
    assert all(r.hint is not None for r in result.battles if not r.is_brain_battle)
    # 交換しないので、レンタルの回数（7周）だけ数える
    assert challenge.rent_trade_count == 7


def test_trade_replaces_member_and_counts(monkeypatch):
    always_win(monkeypatch)
    agent = RandomAgent(random.Random(0), trade_chance=1.0)
    challenge = FactoryChallenge(rules.LEVEL_OPEN, agent, random.Random(0))
    record = challenge.play_next_battle()
    mine, theirs = record.trade
    assert challenge.player_team[mine] is challenge.last_opponent_team[theirs]
    assert challenge.rent_trade_count == 2
    # 7戦目の後は交換しない
    challenge.run(max_battles=7)
    assert challenge.records[6].trade is None
    assert challenge.rent_trade_count == 1 + 6


def test_loss_ends_challenge(monkeypatch):
    monkeypatch.setattr(challenge_module, "run_battle", lambda *args, **kwargs: BattleResult(won=False, turns=1))
    challenge = FactoryChallenge(rules.LEVEL_50, RandomAgent(random.Random(0)), random.Random(0))
    result = challenge.run()
    assert result.win_streak == 0 and len(result.battles) == 1 and challenge.is_over
    with pytest.raises(RuntimeError):
        challenge.play_next_battle()


# 同じシードなら同じ結果になる（対戦エンジンはまだrandomモジュールを使うので、そちらも固定する）
def test_same_seed_same_result():
    def play(seed):
        random.seed(seed)
        challenge = FactoryChallenge(rules.LEVEL_50, RandomAgent(random.Random(seed), 0.1, 0.5), random.Random(seed))
        result = challenge.run(max_battles=20)
        return [(r.player_team, r.opponent_team, r.won, r.turns) for r in result.battles]

    for seed in range(5):
        assert play(seed) == play(seed)


# 相手側の観測には、持ち物・特性・まだ使っていない技が入らない
class RecordingAgent(RandomAgent):
    def __init__(self):
        super().__init__(random.Random(0), switch_chance=0.2)
        self.turns = []
        self.replacements = []

    def choose_action(self, observation):
        self.turns.append(observation)
        return super().choose_action(observation)

    def choose_replacement(self, observation):
        self.replacements.append(observation)
        return observation.switch_options[-1]


def test_battle_observations_hide_opponent_details():
    random.seed(0)
    generator_rng = random.Random(0)
    from factory.generator import FactoryGenerator
    generator = FactoryGenerator(rules.LEVEL_50)
    context = FactoryContext(rules.LEVEL_50, 0, 1, 1, 1)
    agent = RecordingAgent()
    for _ in range(10):
        team = generator.generate_rentals(generator_rng, 1, 1)
        run_battle(team[:3], team[3:], agent, context)

    assert agent.turns and agent.replacements
    for observation in agent.turns:
        assert isinstance(observation, TurnObservation)
        assert not hasattr(observation.opponent_active, "item")
        assert not hasattr(observation.opponent_active, "moves")
        assert 0 <= observation.opponent_active.hp_ratio <= 1
        assert len(observation.opponent_active.revealed_moves) <= 4
        assert observation.move_options
    # 対戦が進めば、相手の技が判明していく
    assert any(observation.opponent_active.revealed_moves for observation in agent.turns)
    assert all(o.switch_options for o in agent.replacements)


def test_battle_template_is_not_modified():
    random.seed(0)
    from factory.generator import FactoryGenerator
    team = FactoryGenerator(rules.LEVEL_50).generate_rentals(random.Random(0), 1, 1)
    hp_before = [mon.template.current_status.current_hp for mon in team]
    run_battle(team[:3], team[3:], RandomAgent(random.Random(0)), FactoryContext(rules.LEVEL_50, 0, 1, 1, 1))
    assert [mon.template.current_status.current_hp for mon in team] == hp_before


# エンジンのフック: move_policy で技を選べる・replacement_policy で交代先を選べる
def test_engine_move_and_replacement_policy():
    chosen_names = []

    def move_policy(battle, trainer, options):
        chosen_names.append(options[-1].name)
        return options[-1]

    replacement_calls = []

    def replacement_policy(battle, trainer):
        replacement_calls.append(trainer.find_switch_candidates())
        return trainer.find_switch_candidates()[-1]

    random.seed(1)
    for _ in range(20):
        player = Trainer([Pokemon(i, 0) for i in (0, 1, 2)], move_policy=move_policy,
                         replacement_policy=replacement_policy)
        opponent = Trainer([Pokemon(i, 0) for i in (3, 4, 5)])
        Battle(player, opponent).start_battle()
    assert chosen_names and replacement_calls
    # 2体残っている状態で1体目が倒れたら、後ろの方（インデックス2）を出す
    assert any(candidates == [1, 2] for candidates in replacement_calls)
