from battlelogic.item import IRON_BALL
from readpokemondata import load_type_chart_data, load_type_data

# みやぶるでゴースト無効化を無視する対象タイプ（ノーマル/かくとう技がゴーストタイプに無効化される仕様の解除用）
TYPE_ID_NORMAL = 0
TYPE_ID_FIGHTING = 6
TYPE_ID_GHOST = 13
TYPE_ID_GROUND = 8
TYPE_ID_FLYING = 9

_name_to_id = None


def _get_name_to_id():
    global _name_to_id
    if _name_to_id is None:
        name_to_id = {}
        for type_id, name in load_type_data().items():
            name_to_id[name] = int(type_id)
        _name_to_id = name_to_id
    return _name_to_id


def resolve_type_id(type_name_or_id):
    if isinstance(type_name_or_id, int):
        return type_name_or_id
    return _get_name_to_id()[type_name_or_id]


def get_multiplier(attack_type, defend_type) -> float:
    attack_id = resolve_type_id(attack_type)
    defend_id = resolve_type_id(defend_type)

    row = load_type_chart_data().get(str(attack_id))
    if row is None:
        return 1.0

    multiplier = row.get(str(defend_id))
    if multiplier is None:
        return 1.0
    return multiplier


def get_effectiveness(attack_type, defend_type1, defend_type2=None) -> float:
    multiplier = get_multiplier(attack_type, defend_type1)
    if defend_type2 is not None:
        multiplier *= get_multiplier(attack_type, defend_type2)
    return multiplier


# moveがis_typeless(わるあがき等)なら常に等倍。そうでなければ通常通りタイプ相性を計算する
# ignore_ghost_immunity=True（みやぶる済みの相手）かつノーマル/かくとう技の場合は、
# 相手のゴーストタイプを無いものとして相性を計算する（ゴースト無効化の解除）
# 相手がくろいてっきゅうを持っている場合、じめん技は相手のひこうタイプを無いものとして相性を計算する
def get_move_effectiveness(move, defender, ignore_ghost_immunity=False) -> float:
    if move.is_typeless:
        return 1.0

    attack_id = resolve_type_id(move.type)

    ignored_type_ids = set()
    if ignore_ghost_immunity and attack_id in (TYPE_ID_NORMAL, TYPE_ID_FIGHTING):
        ignored_type_ids.add(TYPE_ID_GHOST)
    if attack_id == TYPE_ID_GROUND and defender.item == IRON_BALL:
        ignored_type_ids.add(TYPE_ID_FLYING)

    if ignored_type_ids:
        defend_types = [
            t for t in (defender.type1, defender.type2)
            if t is not None and t not in ignored_type_ids
        ]
        if not defend_types:
            return 1.0
        multiplier = 1.0
        for defend_type in defend_types:
            multiplier *= get_multiplier(attack_id, defend_type)
        return multiplier

    return get_effectiveness(move.type, defender.type1, defender.type2)


def describe_effectiveness(multiplier: float) -> str:
    if multiplier == 0:
        return "こうかがない"
    if multiplier < 1:
        return "いまひとつ"
    if multiplier > 1:
        return "こうかはばつぐん"
    return "普通"
