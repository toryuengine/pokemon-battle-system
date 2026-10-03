# ベースライン：すべての判断を、選べる選択肢の中からランダムに行うAgent（CLAUDE.md 6節の1）
import random
from typing import List, Optional, Tuple

from factory.agent import Action, FactoryAgent
from factory.observation import (OrderObservation, RentalObservation, ReplacementObservation, TradeObservation,
                                 TurnObservation)
from factory.rules import TEAM_SIZE


class RandomAgent(FactoryAgent):
    # switch_chance: 交代できるターンに交代を選ぶ確率。trade_chance: 勝利後に交換する確率
    def __init__(self, rng: random.Random, switch_chance: float = 0.0, trade_chance: float = 0.0):
        self.rng = rng
        self.switch_chance = switch_chance
        self.trade_chance = trade_chance

    def choose_rentals(self, observation: RentalObservation) -> List[int]:
        return self.rng.sample(range(len(observation.candidates)), TEAM_SIZE)

    def choose_order(self, observation: OrderObservation) -> List[int]:
        order = list(range(len(observation.team)))
        self.rng.shuffle(order)
        return order

    def choose_action(self, observation: TurnObservation) -> Action:
        if observation.switch_options and self.rng.random() < self.switch_chance:
            return Action.switch(self.rng.choice(observation.switch_options))
        return Action.move(self.rng.randrange(len(observation.move_options)))

    def choose_replacement(self, observation: ReplacementObservation) -> int:
        return self.rng.choice(observation.switch_options)

    def choose_trade(self, observation: TradeObservation) -> Optional[Tuple[int, int]]:
        if self.rng.random() >= self.trade_chance:
            return None
        return self.rng.randrange(len(observation.team)), self.rng.randrange(len(observation.opponents))
