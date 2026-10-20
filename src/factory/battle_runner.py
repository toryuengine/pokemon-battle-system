"""ファクトリーの1戦を、Agent に判断させながら対戦エンジンで行う。

対戦エンジンの3つの口（Trainer.switch_policy・move_policy・replacement_policy）を Agent の
choose_action・choose_replacement に繋ぐ。エンジンは毎ターン「交代するか」→「どの技か」の順に聞くので、
交代を聞かれたときに Agent に行動を1つ選ばせ、技を選んだならそれを覚えておいて技選択のときに返す。
交代できないターン（くろいまなざし等）は、技選択のときに初めて Agent に聞く。
技が固定されていて交代もできないターン（溜め技・げきりん等）は、Agent には聞かない。
対戦が終わったら、Agent に on_battle_end があれば最後の経過と結果を渡す。
"""
import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

from battlelogic.battle import Battle
from factory.generation import FactoryPokemon
from factory.hint import Hint
from battlelogic.events import BattleEvent
from factory.observation import (ACTION_SWITCH, OWNER_OPPONENT, OWNER_OWN, BattleEndObservation, FactoryContext,
                                 MoveView, OpponentPokemonView, OwnPokemonView, SideConditions, TurnAction,
                                 TurnObservation, VisibleEvent)
from pokemon import Pokemon
from trainer import Trainer

STAGE_NAMES = ("atk", "defense", "spatk", "spdef", "spd", "accuracy", "evasion")


# 場に出ている個体の、見て分かる一時的な状態の名前と、その判定
VOLATILE_FLAGS = (
    ("confused", lambda status: status.confusion_turns_remaining > 0),
    ("substitute", lambda status: status.substitute_hp > 0),
    ("seeded", lambda status: status.is_seeded),
    ("cursed", lambda status: status.is_cursed),
    ("ingrained", lambda status: status.is_ingrained),
    ("aqua_ring", lambda status: status.has_aqua_ring),
    ("taunted", lambda status: status.taunt_turns_remaining > 0),
    ("encored", lambda status: status.encore_move is not None),
    ("disabled", lambda status: status.disabled_move is not None),
    ("tormented", lambda status: status.is_tormented),
    ("perish_song", lambda status: status.perish_turns_remaining > 0),
    ("drowsy", lambda status: status.yawn_turns_remaining > 0),
    ("infatuated", lambda status: status.infatuated_by is not None),
    ("trapped", lambda status: status.trapped_by is not None),
    ("bound", lambda status: status.bound_turns_remaining > 0),
    ("charging", lambda status: status.charging_move is not None),
    ("recharging", lambda status: status.must_recharge),
)


@dataclass
class _OpponentRecord:
    revealed_move_ids: List[int]
    revealed_item_id: Optional[int] = None


# 相手側（side）について、対戦の経過（Battle.events）から見えた情報を集める
# 場に出てきた個体・使った技・判明した持ち物を、イベントを読み進めながら貯めていく
class OpponentKnowledge:
    def __init__(self, side: int):
        self.side = side
        self.records: Dict[int, _OpponentRecord] = {}
        self._next_event_index = 0

    def update(self, battle: Battle):
        events = battle.events
        for event in events[self._next_event_index:]:
            if event.side != self.side:
                continue
            if event.kind == "switch_in":
                self.records.setdefault(event.data["party_index"], _OpponentRecord([]))
            elif event.kind == "move":
                move_id = event.data["move_id"]
                record = self.records[event.data["party_index"]]
                # わるあがき（-1）はセットの技ではないので数えない
                if move_id >= 0 and move_id not in record.revealed_move_ids:
                    record.revealed_move_ids.append(move_id)
            elif event.kind == "item":
                record = self.records.setdefault(event.data["party_index"], _OpponentRecord([]))
                # 最初に持ち物が変わったとき（消費・はたきおとす・トリック等）の、変わる前の持ち物が元の持ち物
                if record.revealed_item_id is None and event.data["before"] is not None:
                    record.revealed_item_id = event.data["before"]
        self._next_event_index = len(events)


# BattleEvent を、side の側のプレイヤーから見える VisibleEvent にする（観測の new_events）
def to_visible_event(event: BattleEvent, side: int) -> VisibleEvent:
    owner = None if event.side is None else (OWNER_OWN if event.side == side else OWNER_OPPONENT)
    data = dict(event.data)
    party_index = data.pop("party_index", None)
    if event.kind == "switch_in":
        data.pop("indivisual_id", None)
    elif event.kind == "move_result":
        data.pop("damage", None)
    elif event.kind == "hp" and owner == OWNER_OPPONENT:
        max_hp = data["max_hp"]
        data = {"before_ratio": data["before"] / max_hp, "after_ratio": data["after"] / max_hp}
    elif event.kind == "battle_end":
        winner_side = data.pop("winner_side")
        data["won"] = winner_side == side
    return VisibleEvent(event.turn, event.kind, owner, party_index, data)


def _stages_of(battle: Battle, pokemon: Pokemon) -> Dict[str, int]:
    stages = battle.get_stages(pokemon)
    return {name: getattr(stages, name) for name in STAGE_NAMES}


def _volatile_of(pokemon: Pokemon) -> tuple:
    return tuple(name for name, check in VOLATILE_FLAGS if check(pokemon.current_status))


def _side_conditions(trainer: Trainer) -> SideConditions:
    return SideConditions(trainer.reflect_turns_remaining, trainer.light_screen_turns_remaining,
                          trainer.safeguard_turns_remaining, trainer.stealth_rock, trainer.spikes, trainer.toxic_spikes)


def _own_view(party_index: int, spec: FactoryPokemon, pokemon: Pokemon, is_active: bool) -> OwnPokemonView:
    status = pokemon.status
    return OwnPokemonView(
        party_index=party_index,
        pokemon=spec,
        current_hp=pokemon.current_status.current_hp,
        max_hp=status.hp,
        status_condition=pokemon.current_status.status_condition,
        item_id=pokemon.item.id if pokemon.item is not None else None,
        ability_id=pokemon.ability.id,
        moves=tuple(MoveView(slot, move.id, move.current_pp, move.pp) for slot, move in enumerate(pokemon.moves)),
        stats={"hp": status.hp, "atk": status.atk, "defense": status.defense, "spatk": status.spatk,
               "spdef": status.spdef, "spd": status.spd},
        is_active=is_active,
    )


# 対戦の片側（side）を Agent に判断させるための、エンジンの3つの口の実装
class AgentSide:
    def __init__(self, agent, side: int, team: Sequence[FactoryPokemon], context: FactoryContext,
                 hint: Optional[Hint]):
        self.agent = agent
        self.side = side
        self.team = list(team)
        self.context = context
        self.hint = hint
        self.knowledge = OpponentKnowledge(3 - side)
        # 交代を聞いたときに Agent が技を選んだ場合の、(ターン数, 技の位置)
        self._pending_move = None
        # 次の観測の new_events に入れる、battle.events の位置
        self._next_visible_index = 0

    def make_trainer(self) -> Trainer:
        return Trainer([spec.build() for spec in self.team], switch_policy=self.switch_policy,
                       move_policy=self.move_policy, replacement_policy=self.replacement_policy)

    # ---- 観測 ----

    # 前回の観測から今までの、見える出来事
    def take_new_events(self, battle: Battle) -> tuple:
        events = battle.events
        visible = tuple(to_visible_event(event, self.side) for event in events[self._next_visible_index:])
        self._next_visible_index = len(events)
        return visible

    def notify_battle_end(self, battle: Battle, won: bool, is_draw: bool, timed_out: bool):
        on_battle_end = getattr(self.agent, "on_battle_end", None)
        if on_battle_end is not None:
            on_battle_end(BattleEndObservation(self.context, won, is_draw, timed_out, battle.turn,
                                               self.take_new_events(battle)))

    def observe(self, battle: Battle, legal_actions: Sequence[TurnAction]) -> TurnObservation:
        self.knowledge.update(battle)
        own = battle.trainer1 if self.side == 1 else battle.trainer2
        opponent = battle.trainer2 if self.side == 1 else battle.trainer1
        opponent_seen = []
        for party_index in sorted(self.knowledge.records):
            record = self.knowledge.records[party_index]
            pokemon = opponent.party[party_index]
            opponent_seen.append(OpponentPokemonView(
                party_index=party_index,
                pokemon_id=pokemon.pokemon_id,
                types=(pokemon.type1, pokemon.type2),
                hp_ratio=pokemon.current_status.current_hp / pokemon.status.hp,
                status_condition=pokemon.current_status.status_condition,
                revealed_move_ids=tuple(record.revealed_move_ids),
                revealed_item_id=record.revealed_item_id,
                is_active=party_index == opponent.active_index,
            ))
        return TurnObservation(
            context=self.context,
            hint=self.hint,
            turn=battle.turn,
            own_team=tuple(_own_view(index, spec, own.party[index], index == own.active_index)
                           for index, spec in enumerate(self.team)),
            own_active_index=own.active_index,
            own_stages=_stages_of(battle, own.active),
            opponent_team_size=len(opponent.party),
            opponent_seen=tuple(opponent_seen),
            opponent_active_index=opponent.active_index,
            opponent_stages=_stages_of(battle, opponent.active),
            own_volatile=_volatile_of(own.active),
            opponent_volatile=_volatile_of(opponent.active),
            own_side=_side_conditions(own),
            opponent_side=_side_conditions(opponent),
            weather=battle.weather,
            trick_room_turns=battle.trick_room_turns_remaining,
            legal_actions=tuple(legal_actions),
            new_events=self.take_new_events(battle),
        )

    # 場の個体が今出せる技を、行動（技の位置）の一覧にする。わるあがきしか出せなければ TurnAction.move(None) だけ
    @staticmethod
    def _move_actions(battle: Battle, pokemon: Pokemon) -> List[TurnAction]:
        moves, _ = battle.get_selectable_moves(pokemon)
        if not moves:
            return [TurnAction.move(None)]
        return [TurnAction.move(slot) for slot, move in enumerate(pokemon.moves) if any(move is m for m in moves)]

    def _ask_action(self, battle: Battle, legal_actions: List[TurnAction]) -> TurnAction:
        action = self.agent.choose_action(self.observe(battle, legal_actions))
        if action not in legal_actions:
            raise ValueError(f"choose_action returned {action!r}, which is not in {legal_actions!r}")
        return action

    # ---- エンジンの口 ----

    def switch_policy(self, battle: Battle, trainer: Trainer) -> Optional[int]:
        legal_actions = self._move_actions(battle, trainer.active) + \
            [TurnAction.switch(index) for index in trainer.find_switch_candidates()]
        action = self._ask_action(battle, legal_actions)
        if action.kind == ACTION_SWITCH:
            self._pending_move = None
            return action.index
        self._pending_move = (battle.turn, action.index)
        return None

    def move_policy(self, battle: Battle, trainer: Trainer, usable_moves):
        if self._pending_move is not None and self._pending_move[0] == battle.turn:
            slot = self._pending_move[1]
        else:
            slot = self._ask_action(battle, self._move_actions(battle, trainer.active)).index
        self._pending_move = None
        return trainer.active.moves[slot]

    def replacement_policy(self, battle: Battle, trainer: Trainer, candidates: List[int], reason: str) -> int:
        legal_actions = [TurnAction.switch(index) for index in candidates]
        index = self.agent.choose_replacement(self.observe(battle, legal_actions), reason)
        if index not in candidates:
            raise ValueError(f"choose_replacement returned {index!r}, which is not in {candidates!r}")
        return index


@dataclass
class FactoryBattleResult:
    won: bool
    # 同時全滅（プレイヤーの負けとして扱う）
    is_draw: bool
    # ターン上限に達して決着しなかった（プレイヤーの負けとして扱う）
    timed_out: bool
    turns: int
    battle: Battle


# プレイヤー（side 1）と相手（side 2）で1戦行う。チームは先発から順に並べて渡す。
# opponent_agentがNoneなら、相手はエンジンのデフォルト（技はランダム、自分からは交代しない、瀕死時は手持ち順）
# 引き分け（同時全滅）とターン上限は、プレイヤーの負けとして扱う（仕様書10節）
def run_factory_battle(player_team: Sequence[FactoryPokemon], player_agent,
                       opponent_team: Sequence[FactoryPokemon], context: FactoryContext, hint: Optional[Hint],
                       rng: random.Random, opponent_agent=None) -> FactoryBattleResult:
    player_side = AgentSide(player_agent, 1, player_team, context, hint)
    player = player_side.make_trainer()
    opponent_side = None
    if opponent_agent is None:
        opponent = Trainer([spec.build() for spec in opponent_team])
    else:
        opponent_side = AgentSide(opponent_agent, 2, opponent_team, context, None)
        opponent = opponent_side.make_trainer()

    battle = Battle(player, opponent, rng=rng)
    battle.start_battle()
    winner = battle.get_winning_trainer(draw_winner=opponent)
    result = FactoryBattleResult(
        won=winner is player,
        is_draw=player.is_defeated() and opponent.is_defeated(),
        timed_out=winner is None,
        turns=battle.turn,
        battle=battle,
    )
    player_side.notify_battle_end(battle, result.won, result.is_draw, result.timed_out)
    if opponent_side is not None:
        # 相手の Agent から見た勝ち負け（同時全滅・ターン上限は、プレイヤーの負け＝相手の勝ちとして扱う）
        opponent_side.notify_battle_end(battle, not result.won, result.is_draw, result.timed_out)
    return result
