"""ファクトリーの進行状態（仕様書12節）。"""
from dataclasses import dataclass, field
from typing import Dict, List

from factory import rules
from factory.generation import FactoryPokemon


# 挑戦の進行状態。連勝・周・レンタル＋交換の累計回数は負けると0に戻り、BP・プリントは挑戦をまたいで残る
# モードはシングル・オープンレベルだけを扱う（CLAUDE.md 2節）ので持たない
@dataclass
class FactoryState:
    win_streak: int = 0
    # 「レンタル＋交換」の累計回数（強いポケモンの数の判定に使う。最初のレンタルも1回と数える）
    rent_trade_count: int = 0
    # 自分の手持ち（並び順どおり。先頭が先発）
    player_team: List[FactoryPokemon] = field(default_factory=list)
    # 直前に戦った相手のチーム（交換の候補）
    last_opponent_team: List[FactoryPokemon] = field(default_factory=list)
    prints: Dict[str, bool] = field(default_factory=lambda: {"silver": False, "gold": False})
    bp: int = 0

    # 次の対戦が何周目か
    @property
    def round_number(self) -> int:
        return rules.round_number_of(self.win_streak)

    # 次の対戦が周の何戦目か（1〜7）
    @property
    def battle_in_round(self) -> int:
        return rules.battle_in_round_of(self.win_streak)

    # 次の対戦が連勝の何戦目か（1始まり）
    @property
    def battle_number(self) -> int:
        return self.win_streak + 1

    # 負けたときに、連勝に結びついた状態を0に戻す（BP・プリントは残す）
    def reset_streak(self):
        self.win_streak = 0
        self.rent_trade_count = 0
        self.player_team = []
        self.last_opponent_team = []
