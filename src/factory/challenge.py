"""ファクトリーの挑戦の進行（仕様書3節）。

レンタル → （ヒント → 並び順 → 対戦 → 勝てば全回復 → 交換）×7 → 周クリア・BP → 次の周のレンタル…を、
負けるまで繰り返す。判断（レンタル・並び順・ターンの行動・交換）はすべて Agent に聞き、ここでは決めない。

Agent は次のメソッドを持つ（agents/base.py の FactoryAgent）。factory は agents を import しない:
    choose_rentals(RentalObservation) -> 候補の位置3つ
    choose_order(OrderObservation) -> 手持ちの位置の並べ替え（先頭が先発）
    choose_action(TurnObservation) -> TurnAction
    choose_replacement(TurnObservation, reason) -> 手持ちの位置
    choose_trade(TradeObservation) -> None（交換しない）か (自分の位置, 相手の位置)
"""
import random
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from factory import rules
from factory.battle_runner import FactoryBattleResult, run_factory_battle
from factory.generation import FactoryPokemon, generate_opponent_team, generate_rental_candidates
from factory.hint import Hint, make_hint
from factory.observation import FactoryContext, OrderObservation, RentalObservation, TradeObservation
from factory.state import FactoryState


# 1戦の記録
@dataclass
class BattleRecord:
    battle_number: int
    round_number: int
    battle_in_round: int
    nejiki: Optional[str]
    won: bool
    is_draw: bool
    timed_out: bool
    turns: int
    player_team: List[FactoryPokemon]
    opponent_team: List[FactoryPokemon]
    hint: Hint
    # 勝った後に交換したなら (自分の位置, 相手の位置)
    trade: Optional[tuple] = None


# 1回の挑戦（負けるまで、または上限まで）の記録
@dataclass
class ChallengeResult:
    # 最終的な連勝数（負けた対戦は含まない）
    win_streak: int
    # 負けて終わったか（Falseならmax_battlesで打ち切った）
    lost: bool
    bp_earned: int
    battles: List[BattleRecord] = field(default_factory=list)

    @property
    def rounds_cleared(self) -> int:
        return self.win_streak // rules.BATTLES_PER_ROUND


class FactoryChallenge:
    # rngはポケモンの生成と対戦の乱数（シードを固定すれば、同じ判断をする Agent なら同じ挑戦になる）
    # opponent_agentがNoneなら、相手はエンジンのデフォルト（ランダムな技選択）で戦う
    def __init__(self, agent, rng: random.Random, state: Optional[FactoryState] = None, opponent_agent=None):
        self.agent = agent
        self.rng = rng
        self.state = state if state is not None else FactoryState()
        self.opponent_agent = opponent_agent

    def context(self) -> FactoryContext:
        state = self.state
        return FactoryContext(
            round_number=state.round_number,
            battle_in_round=state.battle_in_round,
            win_streak=state.win_streak,
            battle_number=state.battle_number,
            rent_trade_count=state.rent_trade_count,
            is_nejiki=rules.nejiki_kind(state.battle_number) is not None,
        )

    # ---- 1つずつの段階 ----

    # 周の始めのレンタル。候補6体から Agent が3体を選ぶ
    def rent(self):
        state = self.state
        candidates = generate_rental_candidates(state.round_number, state.rent_trade_count, self.rng)
        chosen = list(self.agent.choose_rentals(RentalObservation(self.context(), tuple(candidates))))
        if len(chosen) != rules.TEAM_SIZE or len(set(chosen)) != rules.TEAM_SIZE \
                or not all(0 <= index < len(candidates) for index in chosen):
            raise ValueError(f"choose_rentals returned {chosen!r}")
        state.player_team = [candidates[index] for index in chosen]
        state.rent_trade_count += 1

    # 次の対戦を行う。相手の生成 → ヒント → 並び順 → 対戦 → 進行状態の更新
    def play_battle(self) -> BattleRecord:
        state = self.state
        context = self.context()
        nejiki = rules.nejiki_kind(context.battle_number)
        opponent_team = generate_opponent_team(context.round_number, context.battle_in_round,
                                               context.battle_number, state.player_team, self.rng)
        hint = make_hint(context.round_number, opponent_team)

        order = list(self.agent.choose_order(OrderObservation(context, tuple(state.player_team), hint)))
        if sorted(order) != list(range(len(state.player_team))):
            raise ValueError(f"choose_order returned {order!r}")
        state.player_team = [state.player_team[index] for index in order]

        # 対戦のたびにポケモンを作り直すので、勝った後の全回復は自然に行われる
        result: FactoryBattleResult = run_factory_battle(state.player_team, self.agent, opponent_team, context, hint,
                                                         self.rng, opponent_agent=self.opponent_agent)
        record = BattleRecord(context.battle_number, context.round_number, context.battle_in_round, nejiki,
                              result.won, result.is_draw, result.timed_out, result.turns,
                              list(state.player_team), list(opponent_team), hint)
        state.last_opponent_team = list(opponent_team)
        if not result.won:
            return record

        state.win_streak += 1
        if nejiki is not None:
            state.prints[nejiki] = True
        if context.battle_in_round == rules.BATTLES_PER_ROUND:
            state.bp += rules.bp_for_round(context.round_number)
        return record

    # 第1〜6戦の勝利後の交換。直前の相手の種族だけを見て、Agent が交換するかを決める
    def offer_trade(self) -> Optional[tuple]:
        state = self.state
        opponent_ids = tuple(pokemon.pokemon_id for pokemon in state.last_opponent_team)
        # 交換の判断は「次の対戦」の時点の進み具合で聞く（周・連勝数は勝った後の値）
        trade = self.agent.choose_trade(TradeObservation(self.context(), tuple(state.player_team), opponent_ids))
        if trade is None:
            return None
        own_index, opponent_index = trade
        if not (0 <= own_index < len(state.player_team) and 0 <= opponent_index < len(state.last_opponent_team)):
            raise ValueError(f"choose_trade returned {trade!r}")
        state.player_team[own_index] = state.last_opponent_team[opponent_index]
        state.rent_trade_count += 1
        return own_index, opponent_index

    # ---- 挑戦全体 ----

    # 次の1戦を進める。周の始めならレンタルから行い、第1〜6戦に勝てば交換まで聞く。
    # 負けたら連勝等を0に戻す（BP・プリントは残る）。人間のCLIのように、1戦ずつ結果を見せたいときに使う
    # on_battle_endを渡すと、対戦が終わって連勝・BPを更新した直後（交換を聞く前）に、その戦の記録を渡して呼ぶ
    def play_next(self, on_battle_end: Optional[Callable[[BattleRecord], None]] = None) -> BattleRecord:
        state = self.state
        if state.battle_in_round == 1:
            self.rent()
        battle_in_round = state.battle_in_round
        record = self.play_battle()
        if on_battle_end is not None:
            on_battle_end(record)
        if not record.won:
            state.reset_streak()
        elif rules.can_trade_after(battle_in_round):
            record.trade = self.offer_trade()
        return record

    # 負けるまで（max_battlesを渡したらその戦数まで）挑戦する
    def play_challenge(self, max_battles: Optional[int] = None) -> ChallengeResult:
        state = self.state
        bp_before = state.bp
        battles = []
        while max_battles is None or len(battles) < max_battles:
            battles.append(self.play_next())
            if not battles[-1].won:
                break

        lost = bool(battles) and not battles[-1].won
        # 負けたときは play_next で連勝が0に戻っているので、負けた対戦の番号から連勝数を出す
        win_streak = battles[-1].battle_number - 1 if lost else state.win_streak
        return ChallengeResult(win_streak, lost, state.bp - bp_before, battles)
