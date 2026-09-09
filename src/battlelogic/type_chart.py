from readpokemondata import load_type_chart_data, load_type_data

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


def describe_effectiveness(multiplier: float) -> str:
    if multiplier == 0:
        return "こうかがない"
    if multiplier < 1:
        return "いまひとつ"
    if multiplier > 1:
        return "こうかはばつぐん"
    return "普通"
