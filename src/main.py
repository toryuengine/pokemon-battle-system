from core.battle import Battle
from core.type_chart import describe_effectiveness
from pokemon import Pokemon


def main():
    pokemon1 = Pokemon(1, 2)
    pokemon2 = Pokemon(3, 0)

    battle = Battle(pokemon1, pokemon2)

    print(f"{pokemon1.name} vs {pokemon2.name}")

    turn = 0
    while battle.get_winner() is None:
        attacker, defender = (pokemon1, pokemon2) if turn % 2 == 0 else (pokemon2, pokemon1)
        move = attacker.moves[0]

        result = battle.use_move(attacker, defender, move)

        if not result["hit"]:
            print(f"{attacker.name}の{move.name}!  しかし外れた")
        elif move.category == "変化":
            print(f"{attacker.name}の{move.name}!")
        else:
            print(
                f"{attacker.name}の{move.name}! {defender.name}に{result['damage']}ダメージ "
                f"({describe_effectiveness(result['effectiveness'])})"
            )
            print(f"  {defender.name}の残りHP: {battle.get_current_hp(defender)}")

        turn += 1

    winner = battle.get_winner()
    print(f"{winner.name}の勝ち！")


if __name__ == "__main__":
    main()
