import json
from pathlib import Path
from typing import Dict, List

from pokemon import Move, Pokemon, PokemonStatus


def load_pokemons(pokemon_path, move_path) -> List[Pokemon]:
    with open(pokemon_path, encoding="utf-8") as f:
        pokemon_data = json.load(f)
    with open(move_path, encoding="utf-8") as f:
        move_data = json.load(f)

    moves = {int(move_id): _parse_move(int(move_id), data) for move_id, data in move_data.items()}

    return [
        _parse_pokemon(entry, set_data, moves)
        for entry in pokemon_data
        for set_data in entry["indivisual"]
    ]


def _parse_pokemon(entry, set_data, moves: Dict[int, Move]) -> Pokemon:
    return Pokemon(
        name=entry["name"],
        type1=entry["type1"],
        type2=entry["type2"],
        status=_parse_status(set_data["status"]),
        item=set_data["item"],
        ability=set_data["ability"],
        moves=[moves[move_id] for move_id in set_data["move"]],
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
        print(pokemon.name, [move.name for move in pokemon.moves])
