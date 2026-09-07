import json
from pathlib import Path
from typing import Dict, List

from pokemon import Move, Pokemon, PokemonStatus


def load_pokemons(pokemon_path, move_path) -> List[Pokemon]:
    with open(pokemon_path, encoding="utf-8") as f:
        pokemon_data = json.load(f)
    with open(move_path, encoding="utf-8") as f:
        move_data = json.load(f)

    moves = {}
    for move_id, data in move_data.items():
        moves[int(move_id)] = _parse_move(int(move_id), data)

    pokemons = []
    for entry in pokemon_data:
        for set_data in entry["indivisual"]:
            pokemons.append(_parse_pokemon(entry, set_data, moves))

    return pokemons


def _parse_pokemon(entry, set_data, moves: Dict[int, Move]) -> Pokemon:
    pokemon_moves = []
    for move_id in set_data["move"]:
        pokemon_moves.append(moves[move_id])

    return Pokemon(
        name=entry["name"],
        type1=entry["type1"],
        type2=entry["type2"],
        status=_parse_status(set_data["status"]),
        item=set_data["item"],
        ability=set_data["ability"],
        moves=pokemon_moves,
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


def _parse_move(move_id: int, move_data) -> Move:
    return Move(
        id=move_id,
        name=move_data["name"],
        type=move_data["type"],
        category=move_data["category"],
        power=move_data["power"],
        pp=move_data["pp"],
        hitrate=move_data["hitrate"],
    )


if __name__ == "__main__":
    data_dir = Path(__file__).resolve().parent.parent / "data"
    pokemons = load_pokemons(data_dir / "pokemon.json", data_dir / "move.json")

    print(f"{len(pokemons)}体読み込みました")
    for pokemon in pokemons:
        move_names = []
        for move in pokemon.moves:
            move_names.append(move.name)
        print(pokemon.name, move_names)
