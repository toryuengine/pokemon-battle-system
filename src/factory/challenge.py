# バトルファクトリー（シングル）の挑戦の流れ（3節）。レンタル→（ヒント→並び順→対戦→交換）×7→次の周、を負けるまで繰り返す
# 状態は12節の「実装時に保持すべき状態」に合わせる
import random
from dataclasses import dataclass, field
from typing import List, Optional

from factory import rules
from factory.agent import FactoryAgent
from factory.battle_runner import run_battle
from factory.generator import FactoryGenerator, FactoryMon
from factory.hints import Hint, make_hint
from factory.observation import (FactoryContext, OrderObservation, RentalObservation, TradeObservation, own_view,
                                 species_view)


# 1戦の記録
@dataclass
class BattleRecord:
    battle_number: int      # 連勝の通算で何戦目か（1始まり）
    round_number: int
    battle_in_round: int
    is_brain_battle: bool
    hint: Optional[Hint]
    player_team: List[str]  # 並び順どおりの名前
    opponent_team: List[str]
    won: bool
    turns: int
    trade: Optional[tuple] = None  # 勝利後に交換した(自分のインデックス, 相手のインデックス)


# 挑戦全体の結果
@dataclass
class ChallengeResult:
    win_streak: int
    bp: int
    prints: dict
    battles: List[BattleRecord] = field(default_factory=list)

    @property
    def rounds_cleared(self) -> int:
        return self.win_streak // rules.BATTLES_PER_ROUND


class FactoryChallenge:
    # level: rules.LEVEL_50 / rules.LEVEL_OPEN
    # agent: プレイヤーの判断。opponent_agent: 相手トレーナーの対戦中の判断（Noneならエンジン標準のランダム）
    # rng: レンタル候補・相手チームの生成に使う乱数（対戦エンジン内部の乱数は、まだrandomモジュールを直接使っている）
    def __init__(self, level: str, agent: FactoryAgent, rng: random.Random,
                 opponent_agent: Optional[FactoryAgent] = None, generator: Optional[FactoryGenerator] = None):
        self.level = level
        self.agent = agent
        self.opponent_agent = opponent_agent
        self.rng = rng
        self.generator = generator if generator is not None else FactoryGenerator(level)

        self.win_streak = 0
        # レンタル＋交換の累計回数（強いポケモンの判定用。最初のレンタルを1と数える）
        self.rent_trade_count = 0
        self.player_team: List[FactoryMon] = []
        self.last_opponent_team: List[FactoryMon] = []
        self.prints = {rules.SILVER: False, rules.GOLD: False}
        self.bp = 0
        self.is_over = False
        self.records: List[BattleRecord] = []

    @property
    def round_number(self) -> int:
        return rules.round_of(self.win_streak)

    @property
    def battle_in_round(self) -> int:
        return rules.battle_in_round_of(self.win_streak)

    def context(self) -> FactoryContext:
        return FactoryContext(level=self.level, win_streak=self.win_streak, round_number=self.round_number,
                              battle_in_round=self.battle_in_round, rent_trade_count=self.rent_trade_count)

    # 負けるまで（またはmax_battles戦するまで）挑戦を続ける
    def run(self, max_battles: Optional[int] = None) -> ChallengeResult:
        while not self.is_over and (max_battles is None or len(self.records) < max_battles):
            self.play_next_battle()
        return ChallengeResult(win_streak=self.win_streak, bp=self.bp, prints=dict(self.prints), battles=self.records)

    # 次の1戦を行う（周の最初ならレンタルから）。勝てば交換フェーズまで進める
    def play_next_battle(self) -> BattleRecord:
        if self.is_over:
            raise RuntimeError("挑戦は既に終わっています")
        if self.battle_in_round == 1:
            self.rent()

        battle_number = self.win_streak + 1
        round_number = self.round_number
        battle_in_round = self.battle_in_round
        brain = rules.brain_battle(battle_number)

        opponents = self.generator.generate_opponents(self.rng, battle_number, self.player_team)
        # ネジキはチームを対戦するまで明かさないので、ヒントが無い
        hint = None if brain is not None else make_hint(round_number, opponents)

        order = self.agent.choose_order(OrderObservation(
            context=self.context(), team=tuple(own_view(mon.template) for mon in self.player_team),
            hint=hint, is_brain_battle=brain is not None))
        _check_permutation(order, len(self.player_team))
        self.player_team = [self.player_team[i] for i in order]

        result = run_battle(self.player_team, opponents, self.agent, self.context(), self.opponent_agent)
        record = BattleRecord(
            battle_number=battle_number, round_number=round_number, battle_in_round=battle_in_round,
            is_brain_battle=brain is not None, hint=hint,
            player_team=[mon.name for mon in self.player_team], opponent_team=[mon.name for mon in opponents],
            won=result.won, turns=result.turns,
        )
        self.records.append(record)

        if not result.won:
            self.is_over = True
            return record

        self.win_streak += 1
        self.last_opponent_team = opponents
        if brain is not None:
            self.prints[brain.print_name] = True
        if battle_in_round == rules.BATTLES_PER_ROUND:
            self.bp += rules.bp_for_round(round_number)
        else:
            record.trade = self.offer_trade()
        return record

    # 4節: 周の開始時に6体から3体を選ぶ
    def rent(self):
        self.rent_trade_count += 1
        candidates = self.generator.generate_rentals(self.rng, self.round_number, self.rent_trade_count)
        chosen = self.agent.choose_rentals(RentalObservation(
            context=self.context(), candidates=tuple(own_view(mon.template) for mon in candidates)))
        if len(chosen) != rules.TEAM_SIZE or len(set(chosen)) != rules.TEAM_SIZE \
                or not all(0 <= i < len(candidates) for i in chosen):
            raise ValueError(f"レンタルは候補から異なる{rules.TEAM_SIZE}体を選んでください: {chosen}")
        self.player_team = [candidates[i] for i in chosen]

    # 5節: 勝利後に1回だけ、自分の1体と直前の相手の1体を入れ替えられる（相手は種族しか見えない）
    def offer_trade(self) -> Optional[tuple]:
        trade = self.agent.choose_trade(TradeObservation(
            context=self.context(), team=tuple(own_view(mon.template) for mon in self.player_team),
            opponents=tuple(species_view(mon.template) for mon in self.last_opponent_team)))
        if trade is None:
            return None
        mine, theirs = trade
        if not (0 <= mine < len(self.player_team) and 0 <= theirs < len(self.last_opponent_team)):
            raise ValueError(f"交換するインデックスが範囲外です: {trade}")
        self.player_team[mine] = self.last_opponent_team[theirs]
        self.rent_trade_count += 1
        return trade


def _check_permutation(order: List[int], size: int):
    if sorted(order) != list(range(size)):
        raise ValueError(f"並び順は0〜{size - 1}の並べ替えで指定してください: {order}")
