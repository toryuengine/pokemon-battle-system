from pokemon import Move, Pokemon, PokemonStatus


def main():
    status = PokemonStatus(
        hp=270,
        atk=152,
        defense=171,
        spatk=294,
        spdef=268,
        spd=165,
    )

    moves = [
        Move(id=0, name="リーフストーム", type="くさ", category="特殊", power=140, pp=5, hitrate=90),
        Move(id=1, name="ヘドロばくだん", type="どく", category="特殊", power=90, pp=10, hitrate=100),
        Move(id=2, name="ドわすれ", type="エスパー", category="変化", power=0, pp=20, hitrate=0),
        Move(id=3, name="ねむりごな", type="くさ", category="変化", power=0, pp=15, hitrate=75),
    ]

    pokemon = Pokemon(
        name="フシギバナ",
        type1=4,
        type2=7,
        status=status,
        item=0,
        ability=0,
        moves=moves,
    )

    print(pokemon)
    print(f"名前: {pokemon.name}")
    print(f"HP: {pokemon.status.hp}")
    print(f"技: {[move.name for move in pokemon.moves]}")


if __name__ == "__main__":
    main()
