from pokemon import Pokemon


def main():
    pokemon = Pokemon(1, 2)

    move_names = []
    for move in pokemon.moves:
        move_names.append(move.name)

    print(pokemon)
    print(f"名前: {pokemon.name}")
    print(f"HP: {pokemon.status.hp}")
    print(f"技: {move_names}")


if __name__ == "__main__":
    main()
