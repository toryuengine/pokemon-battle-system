"""AI の Agent の判断をそのまま使いながら、経過と選んだ行動を表示する（観戦モード）。

判断は包んだ Agent に任せ、ここでは観測と結果を文字列にして出すだけ。包んだ Agent に渡す観測も、選ぶ行動も変えないので、
同じシードなら表示しないとき（自動プレイ）と同じ挑戦になる。
"""
from typing import Callable, Optional, Sequence, Tuple

from agents.base import FactoryAgent
from factory.observation import (BattleEndObservation, OrderObservation, RentalObservation, TradeObservation,
                                 TurnAction, TurnObservation)
from interface.narrator import Narrator
from interface.text import action_text, battle_state, context_text, hint_text, pokemon_detail, pokemon_name


class SpectatorAgent(FactoryAgent):
    # pause_fnを渡すと、ターンの行動を選ぶたびに呼ぶ（Enterを待つ等。1ターンずつ見たいとき）
    def __init__(self, agent: FactoryAgent, output_fn: Callable[[str], None] = print,
                 pause_fn: Optional[Callable[[], None]] = None):
        self.agent = agent
        self.output_fn = output_fn
        self.pause_fn = pause_fn
        self.narrator = Narrator()

    def show(self, *lines: str):
        for line in lines:
            self.output_fn(line)

    def choose_rentals(self, observation: RentalObservation) -> Sequence[int]:
        chosen = self.agent.choose_rentals(observation)
        self.show("", f"=== レンタル  {context_text(observation)} ===")
        for index in chosen:
            self.show(*pokemon_detail(observation.candidates[index]))
        return chosen

    def choose_order(self, observation: OrderObservation) -> Sequence[int]:
        self.narrator.reset()
        order = self.agent.choose_order(observation)
        self.show("", f"=== 対戦  {context_text(observation)} ===", "ヒント: " + hint_text(observation.hint),
                  "並び順: " + "・".join(observation.team[index].name for index in order))
        return order

    def _show_turn(self, observation: TurnObservation):
        self.show(*self.narrator.narrate(observation.new_events))
        self.show(*battle_state(observation))

    def choose_action(self, observation: TurnObservation) -> TurnAction:
        self._show_turn(observation)
        action = self.agent.choose_action(observation)
        self.show(f"  → {action_text(action, observation)}")
        if self.pause_fn is not None:
            self.pause_fn()
        return action

    def choose_replacement(self, observation: TurnObservation, reason: str) -> int:
        self._show_turn(observation)
        index = self.agent.choose_replacement(observation, reason)
        self.show(f"  → {action_text(TurnAction.switch(index), observation)}")
        return index

    def choose_trade(self, observation: TradeObservation) -> Optional[Tuple[int, int]]:
        trade = self.agent.choose_trade(observation)
        if trade is None:
            self.show("交換: しない")
        else:
            own_index, opponent_index = trade
            self.show(f"交換: {observation.team[own_index].name} → "
                      f"{pokemon_name(observation.opponent_pokemon_ids[opponent_index])}")
        return trade

    def on_battle_end(self, observation: BattleEndObservation):
        self.show(*self.narrator.narrate(observation.new_events))
        self.agent.on_battle_end(observation)
