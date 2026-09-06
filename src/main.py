from pathlib import Path

from readpokemondata import load_pokemons


def main():
    data_dir = Path(__file__).resolve().parent.parent / "data"
    pokemon = load_pokemons(data_dir / "pokemon.json", data_dir / "move.json")[0]

    print(pokemon)
    print(f"名前: {pokemon.name}")
    print(f"HP: {pokemon.status.hp}")
    print(f"技: {[move.name for move in pokemon.moves]}")


if __name__ == "__main__":
    main()
