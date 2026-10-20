"""人間がCLIで判断する FactoryAgent。

観測を文字列にして見せ、入力で選ばせる。AIと同じ FactoryAgent を実装するので、FactoryChallenge からは区別されない
（CLAUDE.md 3.2節）。入力と出力は関数で差し替えられる（テストでは決まった入力を流し込む）。

advisor に別の Agent を渡すと、判断のたびにその Agent の選択を「助言」として見せる（CLAUDE.md 4節の助言）。
助言の Agent は同じ観測を受け取るだけで、実際の選択には使わない。
"""
import re
from typing import Callable, List, Optional, Sequence, Tuple

from agents.base import FactoryAgent
from factory import rules
from factory.observation import (BattleEndObservation, OrderObservation, RentalObservation, TradeObservation,
                                 TurnAction, TurnObservation)
from interface.narrator import Narrator
from interface.text import action_text, battle_state, context_text, hint_text, pokemon_detail, pokemon_name

QUIT_COMMANDS = ("q", "quit", "exit")
HELP_TEXT = "（q: やめる  d: 自分の手持ちの詳細）"


# 入力で「やめる」が選ばれたとき。挑戦の途中で抜けるために投げる
class QuitGame(Exception):
    pass


def _parse_numbers(text: str) -> Optional[List[int]]:
    tokens = [token for token in re.split(r"[\s,、]+", text.strip()) if token]
    if not tokens or not all(token.isdigit() for token in tokens):
        return None
    return [int(token) for token in tokens]


class HumanAgent(FactoryAgent):
    def __init__(self, input_fn: Callable[[str], str] = input, output_fn: Callable[[str], None] = print,
                 advisor: Optional[FactoryAgent] = None, advisor_name: str = "AI"):
        self.input_fn = input_fn
        self.output_fn = output_fn
        self.advisor = advisor
        self.advisor_name = advisor_name
        self.narrator = Narrator()
        # 対戦中に「d」で見せる自分の手持ち（直近の観測のもの）
        self._last_team = ()

    # ---- 入出力 ----

    def show(self, *lines: str):
        for line in lines:
            self.output_fn(line)

    def _ask(self, prompt: str) -> str:
        while True:
            text = self.input_fn(prompt).strip()
            if text.lower() in QUIT_COMMANDS:
                raise QuitGame()
            if text.lower() == "d":
                for pokemon in self._last_team:
                    self.show(*pokemon_detail(pokemon))
                continue
            return text

    def _advise(self, text: str):
        self.show(f"  助言（{self.advisor_name}）: {text}")

    # ---- 判断 ----

    def choose_rentals(self, observation: RentalObservation) -> Sequence[int]:
        self.show("", f"=== レンタル  {context_text(observation)} ===")
        for number, pokemon in enumerate(observation.candidates, 1):
            lines = pokemon_detail(pokemon)
            self.show(f"{number}. {lines[0]}", *lines[1:])
        if self.advisor is not None:
            advice = self.advisor.choose_rentals(observation)
            self._advise(" ".join(str(index + 1) for index in advice))
        count = len(observation.candidates)
        while True:
            numbers = _parse_numbers(self._ask(f"借りる{rules.TEAM_SIZE}体を、先発から順に番号で（例: 1 3 5） > "))
            if numbers and len(numbers) == rules.TEAM_SIZE and len(set(numbers)) == rules.TEAM_SIZE \
                    and all(1 <= number <= count for number in numbers):
                self._last_team = tuple(observation.candidates[number - 1] for number in numbers)
                return [number - 1 for number in numbers]
            self.show(f"1〜{count}の番号を、重ならないように{rules.TEAM_SIZE}つ入れてください")

    def choose_order(self, observation: OrderObservation) -> Sequence[int]:
        self.narrator.reset()
        self._last_team = observation.team
        self.show("", f"=== 対戦前  {context_text(observation)} ===", "ヒント: " + hint_text(observation.hint))
        for number, pokemon in enumerate(observation.team, 1):
            lines = pokemon_detail(pokemon)
            self.show(f"{number}. {lines[0]}", *lines[1:])
        if self.advisor is not None:
            advice = self.advisor.choose_order(observation)
            self._advise(" ".join(str(index + 1) for index in advice))
        size = len(observation.team)
        while True:
            text = self._ask(f"並び順を番号で（例: 2 1 3。空ならこのまま）{HELP_TEXT} > ")
            if not text:
                return list(range(size))
            numbers = _parse_numbers(text)
            if numbers and sorted(numbers) == list(range(1, size + 1)):
                return [number - 1 for number in numbers]
            self.show(f"1〜{size}を1つずつ並べてください")

    def _show_turn(self, observation: TurnObservation):
        self._last_team = tuple(view.pokemon for view in observation.own_team)
        self.show(*self.narrator.narrate(observation.new_events))
        self.show("", *battle_state(observation))

    def _choose_from(self, observation: TurnObservation, actions: Sequence[TurnAction], prompt: str,
                     advice: Optional[TurnAction]) -> TurnAction:
        for number, action in enumerate(actions, 1):
            self.show(f"  {number}. {action_text(action, observation)}")
        if advice is not None:
            self._advise(action_text(advice, observation))
        while True:
            numbers = _parse_numbers(self._ask(f"{prompt} {HELP_TEXT} > "))
            if numbers and len(numbers) == 1 and 1 <= numbers[0] <= len(actions):
                return actions[numbers[0] - 1]
            self.show(f"1〜{len(actions)}の番号を1つ入れてください")

    def choose_action(self, observation: TurnObservation) -> TurnAction:
        self._show_turn(observation)
        advice = self.advisor.choose_action(observation) if self.advisor is not None else None
        return self._choose_from(observation, observation.legal_actions, "行動を選んでください", advice)

    def choose_replacement(self, observation: TurnObservation, reason: str) -> int:
        self._show_turn(observation)
        advice = None
        if self.advisor is not None:
            advice = TurnAction.switch(self.advisor.choose_replacement(observation, reason))
        prompt = {"faint": "次に出すポケモンは？", "u_turn": "とんぼがえりで交代するポケモンは？",
                  "baton_pass": "バトンタッチで交代するポケモンは？"}.get(reason, "交代するポケモンは？")
        return self._choose_from(observation, observation.legal_actions, prompt, advice).index

    def choose_trade(self, observation: TradeObservation) -> Optional[Tuple[int, int]]:
        self._last_team = observation.team
        self.show("", f"=== 交換  次は {context_text(observation)} ===")
        self.show("自分の手持ち:")
        for number, pokemon in enumerate(observation.team, 1):
            self.show(f"  {number}. {pokemon_detail(pokemon)[0]}")
        self.show("相手の3体（技・持ち物は分からない）:")
        for number, pokemon_id in enumerate(observation.opponent_pokemon_ids, 1):
            self.show(f"  {number}. {pokemon_name(pokemon_id)}")
        if self.advisor is not None:
            advice = self.advisor.choose_trade(observation)
            self._advise("交換しない" if advice is None else
                         f"{advice[0] + 1} と {advice[1] + 1} を交換")
        team_size, opponent_size = len(observation.team), len(observation.opponent_pokemon_ids)
        while True:
            text = self._ask(f"交換するなら「自分の番号 相手の番号」（例: 1 2）、しないなら空 {HELP_TEXT} > ")
            if not text or text.lower() == "n":
                return None
            numbers = _parse_numbers(text)
            if numbers and len(numbers) == 2 and 1 <= numbers[0] <= team_size and 1 <= numbers[1] <= opponent_size:
                return numbers[0] - 1, numbers[1] - 1
            self.show(f"自分は1〜{team_size}、相手は1〜{opponent_size}の番号を入れてください")

    def on_battle_end(self, observation: BattleEndObservation):
        self.show(*self.narrator.narrate(observation.new_events))
        if observation.timed_out:
            self.show("（ターン上限に達したので、負けとして扱います）")
        elif observation.is_draw:
            self.show("（同時に全滅したので、負けとして扱います）")
