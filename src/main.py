from pathlib import Path

from readpokemondata import load_pokemons


def main():
    data_dir = Path(__file__).resolve().parent.parent / "data"
    pokemon = load_pokemons(data_dir / "pokemon.json", data_dir / "move.json")[1]

    move_names = []
    for move in pokemon.moves:
        move_names.append(move.name)

    print(pokemon)
    print(f"名前: {pokemon.name}")
    print(f"HP: {pokemon.status.hp}")
    print(f"技: {move_names}")


if __name__ == "__main__":
    main()
