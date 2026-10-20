"""すべての判断をランダムに行う Agent（ベースライン。CLAUDE.md 6節の1）。"""
import random
from typing import Optional, Sequence, Tuple

from agents.base import FactoryAgent
from factory import rules
from factory.observation import (ACTION_SWITCH, OrderObservation, RentalObservation, TradeObservation, TurnAction,
                                 TurnObservation)


class RandomAgent(FactoryAgent):
    # switch_chanceは、交代できるターンに交代を選ぶ確率。Noneなら技と交代を区別せず、選べる行動から一様に選ぶ
    # trade_chanceは、交換できるときに交換する確率（交換するなら自分・相手の1体を一様に選ぶ）
    def __init__(self, rng: random.Random, switch_chance: Optional[float] = None, trade_chance: float = 0.5):
        self.rng = rng
        self.switch_chance = switch_chance
        self.trade_chance = trade_chance

    def choose_rentals(self, observation: RentalObservation) -> Sequence[int]:
        return self.rng.sample(range(len(observation.candidates)), rules.TEAM_SIZE)

    def choose_order(self, observation: OrderObservation) -> Sequence[int]:
        order = list(range(len(observation.team)))
        self.rng.shuffle(order)
        return order

    def choose_action(self, observation: TurnObservation) -> TurnAction:
        actions = list(observation.legal_actions)
        if self.switch_chance is None:
            return self.rng.choice(actions)
        switches = [action for action in actions if action.kind == ACTION_SWITCH]
        moves = [action for action in actions if action.kind != ACTION_SWITCH]
        if switches and (not moves or self.rng.random() < self.switch_chance):
            return self.rng.choice(switches)
        return self.rng.choice(moves)

    def choose_replacement(self, observation: TurnObservation, reason: str) -> int:
        return self.rng.choice(observation.legal_actions).index

    def choose_trade(self, observation: TradeObservation) -> Optional[Tuple[int, int]]:
        if self.rng.random() >= self.trade_chance:
            return None
        return self.rng.randrange(len(observation.team)), self.rng.randrange(len(observation.opponent_pokemon_ids))
