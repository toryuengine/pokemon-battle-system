import json
from pathlib import Path
from typing import List

from pokemon import Pokemon, PokemonSet, PokemonStatus


def load_pokemons(path) -> List[Pokemon]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    return [_parse_pokemon(entry) for entry in data]


def _parse_pokemon(entry) -> Pokemon:
    indivisual = [_parse_set(set_data) for set_data in entry["indivisual"]]
    return Pokemon(
        name=entry["name"],
        type1=entry["type1"],
        type2=entry["type2"],
        indivisual=indivisual,
    )


def _parse_set(set_data) -> PokemonSet:
    return PokemonSet(
        status=_parse_status(set_data["status"]),
        item=set_data["item"],
        ability=set_data["ability"],
        move=set_data["move"],
    )


def _parse_status(status_data) -> PokemonStatus:
    return PokemonStatus(
        hp=status_data["hp"],
        atk=status_data["atk"],
        defense=status_data["def"],
        spatk=status_data["spatk"],
        spdef=status_data["spdef"],
        spd=status_data["spd"],
    )


if __name__ == "__main__":
    data_path = Path(__file__).resolve().parent.parent / "data" / "pokemon.json"
    pokemons = load_pokemons(data_path)

    print(f"{len(pokemons)}匹読み込みました")
    for pokemon in pokemons:
        print(pokemon.name)
