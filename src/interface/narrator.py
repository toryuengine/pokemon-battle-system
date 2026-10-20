"""見える出来事（VisibleEvent）を、本編の画面のメッセージ風の文字列にする。

どの個体の出来事かは手持ちの位置（party_index）でしか分からないので、場に出てきたときの種族を覚えておいて名前を引く。
1戦ごとに作り直す（reset）。
"""
from typing import Dict, Iterable, List, Optional, Tuple

from factory.observation import OWNER_OPPONENT, VisibleEvent
from interface.text import is_status_move, item_name, move_name, pokemon_name, status_text


class Narrator:
    def __init__(self):
        self.reset()

    def reset(self):
        # (owner, party_index) → 種族ID
        self._species: Dict[Tuple[Optional[str], Optional[int]], int] = {}
        # 直前に出した技（move_result の表示で、変化技かどうかを見るため）
        self._last_move_id: Optional[int] = None

    def _name(self, event: VisibleEvent) -> str:
        pokemon_id = self._species.get((event.owner, event.party_index))
        name = pokemon_name(pokemon_id) if pokemon_id is not None else "？"
        return f"相手の {name}" if event.owner == OWNER_OPPONENT else name

    def narrate(self, events: Iterable[VisibleEvent]) -> List[str]:
        lines = []
        for event in events:
            line = self._line(event)
            if line:
                lines.append(line)
        return lines

    def _line(self, event: VisibleEvent) -> Optional[str]:
        kind = event.kind
        data = event.data
        if kind == "turn_start":
            return f"―― {event.turn}ターン目 ――"
        if kind == "switch_in":
            self._species[(event.owner, event.party_index)] = data["pokemon_id"]
            if event.owner == OWNER_OPPONENT:
                return f"相手は {pokemon_name(data['pokemon_id'])} を くりだした！"
            return f"ゆけっ！ {pokemon_name(data['pokemon_id'])}！"
        if kind == "move":
            self._last_move_id = data["move_id"]
            return f"{self._name(event)} の {move_name(data['move_id'])}！"
        if kind == "move_result":
            return self._move_result(data)
        if kind == "cant_move":
            return f"{self._name(event)} は 動けない！"
        if kind == "hp":
            if "before_ratio" in data:
                return f"  {self._name(event)}  HP {data['before_ratio']:.0%} → {data['after_ratio']:.0%}"
            return f"  {self._name(event)}  HP {data['before']} → {data['after']}/{data['max_hp']}"
        if kind == "faint":
            return f"{self._name(event)} は たおれた！"
        if kind == "status":
            if data["after"]:
                return f"{self._name(event)} は {status_text(data['after'])} になった！"
            return f"{self._name(event)} の {status_text(data['before'])} が なおった！"
        if kind == "item":
            if data["after"] is None:
                return f"{self._name(event)} の {item_name(data['before'])} が なくなった"
            return f"{self._name(event)} の 持ち物が {item_name(data['before'])} から {item_name(data['after'])} に かわった"
        if kind == "battle_end":
            if data.get("is_draw"):
                return "引き分け！"
            return "勝負に 勝った！" if data.get("won") else "勝負に 負けた…"
        return None

    def _move_result(self, data: dict) -> Optional[str]:
        if data.get("charging"):
            return "  （力を ためている）"
        if data.get("blocked_by_protect"):
            return "  まもられた！"
        if data.get("blocked_by_ability"):
            return "  特性で 防がれた！"
        if data.get("blocked_by_substitute"):
            return "  みがわりに 防がれた！"
        if not data.get("hit"):
            # 変化技は hit が立たないこともあるので、外れた・失敗したとは言わない
            return None if is_status_move(self._last_move_id) else "  しかし 当たらなかった／失敗した！"
        parts = []
        effectiveness = data.get("effectiveness", 1.0)
        if effectiveness == 0:
            parts.append("効果が ないようだ…")
        elif effectiveness > 1:
            parts.append("効果は ばつぐんだ！")
        elif effectiveness < 1:
            parts.append("効果は いまひとつのようだ")
        if data.get("hit_substitute"):
            parts.append("みがわりが 攻撃を 受けた！")
        if data.get("hit_count", 0) > 1:
            parts.append(f"{data['hit_count']}回 当たった！")
        return "  " + " ".join(parts) if parts else None
