"""人間向けの表示に使う文字列を作る（IDから名前を引く・ポケモンや観測を文字列にする）。

ここの関数は文字列を返すだけで、print はしない（出力先は呼び出し側が決める）。
"""
from typing import List, Optional, Sequence

from factory import rules
from factory.generation import FactoryPokemon
from factory.hint import Hint
from factory.observation import (ACTION_SWITCH, OpponentPokemonView, OwnPokemonView, SideConditions, TurnAction,
                                 TurnObservation)
from nature import NATURE_NAMES
from readpokemondata import (load_ability_data, load_item_data, load_move_data, load_pokemon_data,
                             load_type_data)

STATUS_NAMES = {
    "burn": "やけど",
    "freeze": "こおり",
    "paralysis": "まひ",
    "poison": "どく",
    "toxic": "もうどく",
    "sleep": "ねむり",
}

WEATHER_NAMES = {"sun": "にほんばれ", "rain": "あめ", "sandstorm": "すなあらし", "hail": "あられ"}

STAGE_LABELS = (("atk", "攻撃"), ("defense", "防御"), ("spatk", "特攻"), ("spdef", "特防"), ("spd", "素早さ"),
                ("accuracy", "命中"), ("evasion", "回避"))

# 実数値の表示の順（OwnPokemonView.stats のキー）
STAT_LABELS = (("hp", "H"), ("atk", "A"), ("defense", "B"), ("spatk", "C"), ("spdef", "D"), ("spd", "S"))

VOLATILE_NAMES = {
    "confused": "こんらん", "substitute": "みがわり", "seeded": "やどりぎ", "cursed": "のろい",
    "ingrained": "ねをはる", "aqua_ring": "アクアリング", "taunted": "ちょうはつ", "encored": "アンコール",
    "disabled": "かなしばり", "tormented": "いちゃもん", "perish_song": "ほろびのうた", "drowsy": "あくび",
    "infatuated": "メロメロ", "trapped": "にげられない", "bound": "しめつけ", "charging": "ため",
    "recharging": "はんどう",
}

GENDER_MARKS = {"male": "♂", "female": "♀"}

CATEGORY_NAMES = {0: "物理", 1: "特殊", 2: "変化"}


# ---- IDから名前 ----

def pokemon_name(pokemon_id: int) -> str:
    return load_pokemon_data()[pokemon_id]["name"]


def move_name(move_id: Optional[int]) -> str:
    if move_id is None or move_id < 0:
        return "わるあがき"
    return load_move_data()[str(move_id)]["name"]


def item_name(item_id: Optional[int]) -> str:
    if item_id is None:
        return "なし"
    return load_item_data()[str(item_id)]


def ability_name(ability_id: int) -> str:
    return load_ability_data()[str(ability_id)]


def type_name(type_id: Optional[int]) -> str:
    return load_type_data()[str(type_id)]


def types_text(types: Sequence[Optional[int]]) -> str:
    return "/".join(type_name(type_id) for type_id in types if type_id is not None)


def status_text(status_condition: Optional[str]) -> str:
    return STATUS_NAMES.get(status_condition, status_condition) if status_condition else ""


# 技の名前・タイプ・分類・威力・命中（"10まんボルト でんき 特殊 95/100"）
def move_detail(move_id: int) -> str:
    data = load_move_data()[str(move_id)]
    power = data["power"] if data["power"] else "-"
    hitrate = data["hitrate"] if data["hitrate"] else "-"
    return f"{data['name']}（{data['type']}・{CATEGORY_NAMES.get(data['category'], '?')}・{power}/{hitrate}）"


def is_status_move(move_id: Optional[int]) -> bool:
    return move_id is not None and move_id >= 0 and load_move_data()[str(move_id)]["category"] == 2


# ---- ポケモン ----

# レンタル候補・自分の手持ちの1体の詳細（セットが全部分かるもの）。複数行
def pokemon_detail(pokemon: FactoryPokemon) -> List[str]:
    built = pokemon.build()
    status = built.status
    gender = GENDER_MARKS.get(pokemon.gender, "")
    nature = NATURE_NAMES[load_pokemon_data()[pokemon.pokemon_id]["indivisual"][pokemon.indivisual_id]["nature"]]
    stats = (f"H{status.hp} A{status.atk} B{status.defense} C{status.spatk} D{status.spdef} S{status.spd}")
    return [
        f"{pokemon.name}{gender} [{types_text(pokemon.types)}] 持ち物:{item_name(pokemon.item_id)} "
        f"特性:{ability_name(pokemon.ability_id)} 性格:{nature} 個体値:{pokemon.iv}",
        f"    {stats}",
        "    技: " + " / ".join(move_detail(move_id) for move_id in pokemon.move_ids),
    ]


def hint_text(hint: Optional[Hint]) -> str:
    if hint is None:
        return "（ヒントなし）"
    if hint.kind == rules.HINT_ALL_NAMES:
        return "相手の3体: " + "・".join(pokemon_name(pokemon_id) for pokemon_id in hint.pokemon_ids)
    if hint.kind == rules.HINT_FIRST_TWO_NAMES:
        return "相手の先頭の2体: " + "・".join(pokemon_name(pokemon_id) for pokemon_id in hint.pokemon_ids)
    if hint.kind == rules.HINT_LEAD_NAME_AND_MOVE:
        return f"相手の先発: {pokemon_name(hint.pokemon_ids[0])}（{move_name(hint.move_id)}を覚えている）"
    if hint.kind == rules.HINT_LEAD_MOVE:
        return f"相手の先発は {move_name(hint.move_id)} を覚えている"
    return f"相手に最も多いタイプ: {type_name(hint.type_id)}"


def stages_text(stages: dict) -> str:
    changed = [f"{label}{stages[key]:+d}" for key, label in STAGE_LABELS if stages.get(key, 0)]
    return " ".join(changed)


def side_text(side: SideConditions) -> str:
    parts = []
    if side.reflect_turns:
        parts.append(f"リフレクター{side.reflect_turns}")
    if side.light_screen_turns:
        parts.append(f"ひかりのかべ{side.light_screen_turns}")
    if side.safeguard_turns:
        parts.append(f"しんぴのまもり{side.safeguard_turns}")
    if side.stealth_rock:
        parts.append("ステルスロック")
    if side.spikes:
        parts.append(f"まきびし×{side.spikes}")
    if side.toxic_spikes:
        parts.append(f"どくびし×{side.toxic_spikes}")
    return " ".join(parts)


def hp_bar(ratio: float, width: int = 20) -> str:
    filled = round(max(0.0, min(1.0, ratio)) * width)
    if ratio > 0 and filled == 0:
        filled = 1
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def _own_line(view: OwnPokemonView) -> str:
    condition = "ひんし" if view.is_fainted else status_text(view.status_condition)
    return (f"{view.pokemon.name} {hp_bar(view.current_hp / view.max_hp)} {view.current_hp}/{view.max_hp}"
            + (f" {condition}" if condition else ""))


def _opponent_line(view: OpponentPokemonView) -> str:
    condition = "ひんし" if view.is_fainted else status_text(view.status_condition)
    line = f"{pokemon_name(view.pokemon_id)} [{types_text(view.types)}] {hp_bar(view.hp_ratio)} {view.hp_ratio:.0%}"
    return line + (f" {condition}" if condition else "")


# 毎ターンの状況（場・両者の場の個体・手持ち）。複数行
def battle_state(observation: TurnObservation) -> List[str]:
    lines = []
    field_parts = []
    if observation.weather:
        field_parts.append(WEATHER_NAMES.get(observation.weather, observation.weather))
    if observation.trick_room_turns:
        field_parts.append(f"トリックルーム{observation.trick_room_turns}")
    if field_parts:
        lines.append("場: " + " ".join(field_parts))

    opponent = observation.opponent_active
    if opponent is not None:
        lines.append("相手: " + _opponent_line(opponent))
        extra = [stages_text(observation.opponent_stages),
                 " ".join(VOLATILE_NAMES.get(name, name) for name in observation.opponent_volatile),
                 side_text(observation.opponent_side)]
        if any(extra):
            lines.append("      " + " ".join(part for part in extra if part))
        known = []
        if opponent.revealed_move_ids:
            known.append("見た技: " + "・".join(move_name(move_id) for move_id in opponent.revealed_move_ids))
        if opponent.revealed_item_id is not None:
            known.append("持ち物: " + item_name(opponent.revealed_item_id))
        if known:
            lines.append("      " + "  ".join(known))
    seen_bench = [view for view in observation.opponent_seen if not view.is_active]
    unseen = observation.opponent_team_size - len(observation.opponent_seen)
    if seen_bench or unseen:
        bench = [_opponent_line(view) for view in seen_bench] + ["？"] * unseen
        lines.append("  相手の控え: " + " / ".join(bench))

    own = observation.own_active
    lines.append("自分: " + _own_line(own))
    extra = [stages_text(observation.own_stages),
             " ".join(VOLATILE_NAMES.get(name, name) for name in observation.own_volatile),
             side_text(observation.own_side)]
    if any(extra):
        lines.append("      " + " ".join(part for part in extra if part))
    bench = [_own_line(view) for view in observation.own_team if not view.is_active]
    if bench:
        lines.append("  自分の控え: " + " / ".join(bench))
    return lines


# 行動の説明（"10まんボルト PP 15/15"・"交代: リザードン"）
def action_text(action: TurnAction, observation: TurnObservation) -> str:
    if action.kind == ACTION_SWITCH:
        view = observation.own_team[action.index]
        return f"交代: {view.pokemon.name}（HP {view.current_hp}/{view.max_hp}）"
    if action.index is None:
        return "わるあがき"
    move = observation.own_active.moves[action.index]
    return f"{move_detail(move.move_id)} PP {move.current_pp}/{move.max_pp}"


def context_text(observation) -> str:
    context = observation.context
    nejiki = "（ネジキ戦）" if context.is_nejiki else ""
    return (f"{context.round_number}周目 第{context.battle_in_round}戦{nejiki}"
            f"  連勝 {context.win_streak}")
