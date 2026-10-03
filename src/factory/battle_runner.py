# ファクトリーの1戦を対戦エンジン（Battle）で行う。対戦中の判断は、Trainerの各policyからAgentに問い合わせる
# Agentには観測（observation.py）だけを渡し、Battleそのものは渡さない
from dataclasses import dataclass
from typing import List, Optional

from battlelogic.battle import Battle
from factory.agent import ACTION_SWITCH, FactoryAgent
from factory.generator import FactoryMon
from factory.observation import (FactoryContext, ReplacementObservation, TurnObservation, move_view,
                                 opponent_view, own_view, stages_dict)
from trainer import Trainer


@dataclass
class BattleResult:
    # プレイヤー側が勝ったか（同時全滅・ターン上限で決着しなかった場合は負け扱い。10節）
    won: bool
    turns: int


# 1人のトレーナーの判断をAgentにつなぐ。Battleからはswitch_policy・move_policy・replacement_policyとして呼ばれる
class AgentController:
    def __init__(self, agent: FactoryAgent, context: FactoryContext):
        self.agent = agent
        self.context = context
        # 相手側のトレーナーと、これまでに場に出てきた相手のポケモン（観測の opponent_seen 用）
        self.opponent_trainer: Optional[Trainer] = None
        self.seen_opponents: List = []
        # 交代の判断を聞いたときにAgentが技を選んでいれば、そのターンの技選択でそれを使う（ターン数とセットで持つ）
        self.pending_move = None

    def attach(self, trainer: Trainer, opponent_trainer: Trainer):
        self.opponent_trainer = opponent_trainer
        trainer.switch_policy = self.switch_policy
        trainer.move_policy = self.move_policy
        trainer.replacement_policy = self.replacement_policy

    # 交代できるターンは、技と交代をまとめてAgentに選ばせる。技を選んだら覚えておき、直後のmove_policyで返す
    def switch_policy(self, battle: Battle, trainer: Trainer) -> Optional[int]:
        options = battle.get_move_options(trainer.active)
        observation = self.turn_observation(battle, trainer, options, tuple(trainer.find_switch_candidates()))
        action = self.agent.choose_action(observation)
        if action.kind == ACTION_SWITCH:
            return action.index
        self.pending_move = (battle.turn, options[action.index])
        return None

    def move_policy(self, battle: Battle, trainer: Trainer, options: list):
        if self.pending_move is not None:
            turn, move = self.pending_move
            self.pending_move = None
            if turn == battle.turn and any(move is option for option in options):
                return move
        # 交代できないターン（溜め中ではないが、くろいまなざし等で逃げられない）は技だけを選ばせる
        observation = self.turn_observation(battle, trainer, options, ())
        return options[self.agent.choose_action(observation).index]

    def replacement_policy(self, battle: Battle, trainer: Trainer) -> int:
        self.note_opponent(battle)
        observation = ReplacementObservation(
            context=self.context,
            team=tuple(own_view(pokemon) for pokemon in trainer.party),
            opponent_active=opponent_view(self.opponent_trainer.active),
            switch_options=tuple(trainer.find_switch_candidates()),
        )
        return self.agent.choose_replacement(observation)

    def note_opponent(self, battle: Battle):
        active = self.opponent_trainer.active
        if all(active is not seen for seen in self.seen_opponents):
            self.seen_opponents.append(active)

    def turn_observation(self, battle: Battle, trainer: Trainer, move_options: list, switch_options: tuple):
        self.note_opponent(battle)
        opponent = self.opponent_trainer
        return TurnObservation(
            context=self.context,
            turn=battle.turn,
            active_index=trainer.active_index,
            team=tuple(own_view(pokemon) for pokemon in trainer.party),
            stat_stages=stages_dict(battle.get_stages(trainer.active)),
            opponent_active=opponent_view(opponent.active),
            opponent_stat_stages=stages_dict(battle.get_stages(opponent.active)),
            opponent_seen=tuple(opponent_view(pokemon) for pokemon in self.seen_opponents),
            opponent_remaining=sum(1 for pokemon in opponent.party if pokemon.current_status.current_hp > 0),
            weather=battle.get_effective_weather(),
            move_options=tuple(move_view(move) for move in move_options),
            switch_options=switch_options,
        )


# player_team・opponent_teamは並び順どおり（先頭が先発）。opponent_agentがNoneなら、相手はエンジン標準の
# 判断（技はランダム・自分からは交代しない）で戦う
def run_battle(player_team: List[FactoryMon], opponent_team: List[FactoryMon], player_agent: FactoryAgent,
               context: FactoryContext, opponent_agent: Optional[FactoryAgent] = None) -> BattleResult:
    player = Trainer([mon.build() for mon in player_team])
    opponent = Trainer([mon.build() for mon in opponent_team])
    AgentController(player_agent, context).attach(player, opponent)
    if opponent_agent is not None:
        AgentController(opponent_agent, context).attach(opponent, player)

    battle = Battle(player, opponent)
    battle.start_battle()
    won = opponent.is_defeated() and not player.is_defeated()
    return BattleResult(won=won, turns=battle.turn)
