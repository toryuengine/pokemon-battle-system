"""バトルファクトリーで判断する主体（Agent）のインターフェース。

プレイヤーが判断する4つの場面（レンタル・並び順・ターンの行動・交換）を1つのクラスにまとめる（CLAUDE.md 3.2節）。
人間（CLI）もAIも、これを実装してファクトリー（factory.challenge.FactoryChallenge）に渡す。
各メソッドに渡るのは観測（factory.observation）だけで、Battle や相手の Pokemon そのものは渡らない。
"""
from abc import ABC, abstractmethod
from typing import Optional, Sequence, Tuple

from factory.observation import BattleEndObservation, OrderObservation, RentalObservation, TradeObservation, TurnAction, TurnObservation


class FactoryAgent(ABC):
    # レンタル：候補6体（observation.candidates）から3体を選び、候補の位置を3つ返す。返した順が手持ちの並びになる
    @abstractmethod
    def choose_rentals(self, observation: RentalObservation) -> Sequence[int]:
        ...

    # 並び順：各戦の前に、自分の3体（observation.team）の並べ替えを返す（例：[2, 0, 1] なら今の3番目が先発）
    @abstractmethod
    def choose_order(self, observation: OrderObservation) -> Sequence[int]:
        ...

    # ターンの行動：observation.legal_actions の中から1つ返す（技か交代）
    @abstractmethod
    def choose_action(self, observation: TurnObservation) -> TurnAction:
        ...

    # 瀕死・とんぼがえり・バトンタッチで次に出す個体を、observation.legal_actions（交代だけが並ぶ）の
    # 交代先の中から選び、手持ちの位置を返す。reasonは"faint"/"u_turn"/"baton_pass"
    @abstractmethod
    def choose_replacement(self, observation: TurnObservation, reason: str) -> int:
        ...

    # 交換：第1〜6戦の勝利後に、交換しないならNone、するなら (自分の手持ちの位置, 相手の位置) を返す
    @abstractmethod
    def choose_trade(self, observation: TradeObservation) -> Optional[Tuple[int, int]]:
        ...

    # 対戦が終わったときに呼ばれる（最後のターンの経過と勝敗）。判断はしないので、必要な Agent だけが上書きする
    def on_battle_end(self, observation: BattleEndObservation):
        pass
