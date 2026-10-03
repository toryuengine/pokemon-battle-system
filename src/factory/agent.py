# ファクトリーでプレイヤーが判断する4つの場面（CLAUDE.md 3.2節）をまとめたインターフェース
# 人間（CLI等）もAIも、このクラスを継承して実装する。factoryは「誰が判断するか」を知らず、ここに問い合わせるだけ
from dataclasses import dataclass
from typing import List, Optional, Tuple

from factory.observation import (OrderObservation, RentalObservation, ReplacementObservation, TradeObservation,
                                 TurnObservation)

ACTION_MOVE = "move"
ACTION_SWITCH = "switch"


# 対戦中の1ターンの行動。kind=ACTION_MOVEならindexはobservation.move_optionsのインデックス、
# kind=ACTION_SWITCHならindexは交代先のチーム内のインデックス（observation.switch_optionsのどれか）
@dataclass(frozen=True)
class Action:
    kind: str
    index: int

    @staticmethod
    def move(index: int) -> "Action":
        return Action(ACTION_MOVE, index)

    @staticmethod
    def switch(index: int) -> "Action":
        return Action(ACTION_SWITCH, index)


class FactoryAgent:
    # 周の開始: レンタル候補6体から3体を選ぶ。candidatesのインデックスを3つ返す（返した順がチームの並び順になる）
    def choose_rentals(self, observation: RentalObservation) -> List[int]:
        raise NotImplementedError

    # 各戦の前: チームの並び順を決める。teamのインデックスの並べ替え（先頭が先発）を返す
    def choose_order(self, observation: OrderObservation) -> List[int]:
        raise NotImplementedError

    # 対戦中の毎ターン: 技か交代を選ぶ
    def choose_action(self, observation: TurnObservation) -> Action:
        raise NotImplementedError

    # 瀕死・とんぼがえり・バトンタッチのとき: 交代先のチーム内のインデックスを返す
    def choose_replacement(self, observation: ReplacementObservation) -> int:
        raise NotImplementedError

    # 第1〜6戦の勝利後: 交換するなら(自分のチームのインデックス, 相手のインデックス)、しないならNoneを返す
    def choose_trade(self, observation: TradeObservation) -> Optional[Tuple[int, int]]:
        raise NotImplementedError
