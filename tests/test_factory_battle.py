"""ファクトリーの1戦（src/factory/battle_runner.py）と、Agent に渡す観測のテスト。"""
import random

import pytest

from agents.random_agent import RandomAgent
from battlelogic.battle import Battle
from factory.battle_runner import AgentSide, run_factory_battle
from factory.generation import make_factory_pokemon
from factory.hint import make_hint
from factory.observation import ACTION_MOVE, ACTION_SWITCH, FactoryContext, TurnAction
from item.itemfactory import create_item
from move.struggle import Struggle
from readpokemondata import load_item_data, load_pokemon_data
from trainer import Trainer

CONTEXT = FactoryContext(round_number=1, battle_in_round=1, win_streak=0, battle_number=1, rent_trade_count=1,
                         is_nejiki=False)


def item_id_of(name):
    return next(int(i) for i, item_name in load_item_data().items() if item_name == name)


def random_team(rng):
    ids = rng.sample(range(len(load_pokemon_data())), 3)
    return [make_factory_pokemon(pokemon_id, rng.randrange(4), 31, rng) for pokemon_id in ids]


# 観測が「見えた情報だけ」になっているかを、真のチームと突き合わせて確かめる Agent
class CheckingAgent(RandomAgent):
    def __init__(self, rng, own_team, opponent_team):
        super().__init__(rng)
        self.own_team = own_team
        self.opponent_team = opponent_team
        self.observations = []
        self.replacements = []

    def check(self, observation):
        self.observations.append(observation)
        assert [view.pokemon for view in observation.own_team] == self.own_team
        assert observation.own_active.is_active
        assert observation.opponent_team_size == 3
        seen_indices = [view.party_index for view in observation.opponent_seen]
        assert observation.opponent_active_index in seen_indices
        for view in observation.opponent_seen:
            truth = self.opponent_team[view.party_index]
            assert view.pokemon_id == truth.pokemon_id
            assert set(view.revealed_move_ids) <= set(truth.move_ids)
            assert view.revealed_item_id in (None, truth.item_id)
            assert view.revealed_ability_id in (None, truth.ability_id)
            assert 0 <= view.hp_ratio <= 1
        # 最初の行動を決める時点では、相手は先発しか見えず、まだ技も見ていない
        if len(self.observations) == 1:
            assert observation.turn == 1
            assert seen_indices == [0]
            assert observation.opponent_seen[0].revealed_move_ids == ()

    def choose_action(self, observation):
        self.check(observation)
        active = observation.own_active
        assert observation.legal_actions
        for action in observation.legal_actions:
            if action.kind == ACTION_SWITCH:
                target = observation.own_team[action.index]
                assert not target.is_active and not target.is_fainted
            elif action.index is not None:
                assert active.moves[action.index].current_pp > 0
        return super().choose_action(observation)

    def choose_replacement(self, observation, reason):
        self.check(observation)
        self.replacements.append(reason)
        assert observation.legal_actions and all(a.kind == ACTION_SWITCH for a in observation.legal_actions)
        return super().choose_replacement(observation, reason)


@pytest.mark.parametrize("seed", range(30))
def test_observations_show_only_visible_information(seed):
    rng = random.Random(seed)
    own, opponent = random_team(rng), random_team(rng)
    agent = CheckingAgent(random.Random(seed), own, opponent)

    result = run_factory_battle(own, agent, opponent, CONTEXT, make_hint(1, opponent), rng)

    assert agent.observations
    battle = result.battle
    assert result.won == (battle.trainer2.is_defeated() and not battle.trainer1.is_defeated())


# 対戦が進めば、相手の使った技・判明した特性・持ち物が観測に貯まっていく
def test_observations_accumulate_revealed_information():
    revealed_moves = revealed_items = revealed_abilities = 0
    for seed in range(30):
        rng = random.Random(seed)
        own, opponent = random_team(rng), random_team(rng)
        agent = CheckingAgent(random.Random(seed), own, opponent)
        run_factory_battle(own, agent, opponent, CONTEXT, None, rng)
        last = agent.observations[-1]
        revealed_moves += sum(len(view.revealed_move_ids) for view in last.opponent_seen)
        revealed_items += sum(view.revealed_item_id is not None for view in last.opponent_seen)
        revealed_abilities += sum(view.revealed_ability_id is not None for view in last.opponent_seen)
    assert revealed_moves > 0 and revealed_items > 0 and revealed_abilities > 0


# 相手も Agent にでき、相手の観測は相手側から見たものになる
def test_opponent_agent_sees_its_own_side():
    rng = random.Random(0)
    own, opponent = random_team(rng), random_team(rng)
    opponent_agent = CheckingAgent(random.Random(1), opponent, own)

    run_factory_battle(own, RandomAgent(random.Random(2)), opponent, CONTEXT, None, rng, opponent_agent=opponent_agent)

    assert opponent_agent.observations


# 選べない行動を返す Agent は誤り
def test_illegal_action_raises():
    class BadAgent(RandomAgent):
        def choose_action(self, observation):
            return TurnAction.switch(observation.own_active_index)

    rng = random.Random(0)
    with pytest.raises(ValueError):
        run_factory_battle(random_team(rng), BadAgent(rng), random_team(rng), CONTEXT, None, rng)


# ---- エンジンの口との繋ぎ ----

class RecordingAgent(RandomAgent):
    def __init__(self, action=None):
        super().__init__(random.Random(0))
        self.action = action
        self.observations = []

    def choose_action(self, observation):
        self.observations.append(observation)
        return self.action if self.action is not None else observation.legal_actions[0]


def make_battle(agent):
    rng = random.Random(0)
    own, opponent = random_team(rng), random_team(rng)
    side = AgentSide(agent, 1, own, CONTEXT, None)
    trainer = side.make_trainer()
    battle = Battle(trainer, Trainer([pokemon.build() for pokemon in opponent]), rng=rng)
    return side, trainer, battle


# 交代できるターンは、技と交代の両方が選べる
def test_switch_policy_offers_moves_and_switches():
    agent = RecordingAgent()
    side, trainer, battle = make_battle(agent)

    battle.choose_switch(trainer)

    actions = agent.observations[0].legal_actions
    assert [a for a in actions if a.kind == ACTION_MOVE] == [TurnAction.move(slot) for slot in range(4)]
    assert [a for a in actions if a.kind == ACTION_SWITCH] == [TurnAction.switch(1), TurnAction.switch(2)]


# 技を選んだら、その技が出る（交代のときに聞いた答えを、技選択で返す）
def test_chosen_move_is_used():
    agent = RecordingAgent(action=TurnAction.move(2))
    side, trainer, battle = make_battle(agent)

    assert battle.choose_switch(trainer) is None
    assert battle.select_move(trainer.active) is trainer.active.moves[2]
    assert len(agent.observations) == 1


# 交代を選んだら、その個体に交代する
def test_chosen_switch_is_used():
    agent = RecordingAgent(action=TurnAction.switch(2))
    side, trainer, battle = make_battle(agent)

    assert battle.choose_switch(trainer) == 2


# 逃げられないターンは、技選択のときに技だけを選ばせる
def test_trapped_pokemon_chooses_only_moves():
    agent = RecordingAgent(action=TurnAction.move(1))
    side, trainer, battle = make_battle(agent)
    trainer.active.current_status.trapped_by = battle.pokemon2

    assert battle.choose_switch(trainer) is None
    assert battle.select_move(trainer.active) is trainer.active.moves[1]
    assert [a.kind for a in agent.observations[0].legal_actions] == [ACTION_MOVE] * 4


# こだわり系で固定されていれば、選べる技は固定された技だけ（交代はできる）
def test_choice_locked_move_is_only_move_action():
    agent = RecordingAgent()
    side, trainer, battle = make_battle(agent)
    active = trainer.active
    active.item = create_item(item_id_of("こだわりスカーフ"))
    active.current_status.choice_locked_move = active.moves[3]

    battle.choose_switch(trainer)

    actions = agent.observations[0].legal_actions
    assert [a for a in actions if a.kind == ACTION_MOVE] == [TurnAction.move(3)]
    assert battle.select_move(active) is active.moves[3]


# PPが尽きたら、わるあがき（TurnAction.move(None)）しか選べない
def test_struggle_action_when_no_pp():
    agent = RecordingAgent()
    side, trainer, battle = make_battle(agent)
    for move in trainer.active.moves:
        move.current_pp = 0

    battle.choose_switch(trainer)

    actions = agent.observations[0].legal_actions
    assert [a for a in actions if a.kind == ACTION_MOVE] == [TurnAction.move(None)]
    assert isinstance(battle.select_move(trainer.active), Struggle)


# 瀕死時の交代先は choose_replacement に聞く
def test_replacement_asks_agent():
    class ReplacementAgent(RecordingAgent):
        def choose_replacement(self, observation, reason):
            self.replacement = (observation.legal_actions, reason)
            return 2

    agent = ReplacementAgent()
    side, trainer, battle = make_battle(agent)
    trainer.active.current_status.current_hp = 0

    battle.resolve_faints()

    assert agent.replacement == ((TurnAction.switch(1), TurnAction.switch(2)), "faint")
    assert trainer.active_index == 2


# ---- Battle.get_selectable_moves（状態を書き換えずに、出せる技を返す） ----

def test_get_selectable_moves():
    agent = RecordingAgent()
    side, trainer, battle = make_battle(agent)
    active = trainer.active
    status = active.current_status

    assert battle.get_selectable_moves(active) == (active.moves, False)

    status.encore_move = active.moves[1]
    assert battle.get_selectable_moves(active) == ([active.moves[1]], True)
    status.encore_move = None

    status.charging_move = active.moves[0]
    assert battle.get_selectable_moves(active) == ([active.moves[0]], True)
    status.charging_move = None

    # こだわり系の持ち物が無ければ、固定は無効（get_selectable_movesは解除はしない）
    status.choice_locked_move = active.moves[2]
    active.item = None
    assert battle.get_selectable_moves(active) == (active.moves, False)
    assert status.choice_locked_move is active.moves[2]
    active.item = create_item(item_id_of("こだわりハチマキ"))
    active.moves[2].current_pp = 0
    assert battle.get_selectable_moves(active) == ([], True)
