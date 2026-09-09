from battlelogic.battle import Battle
from pokemon import Pokemon


def main():
    winrate = {}

    for i in range(10000):
        pokemon1 = Pokemon(1, 2)
        pokemon2 = Pokemon(3, 0)
        battle = Battle(pokemon1, pokemon2)

        battle.start_battle()

        winner = battle.get_winner()
        winrate[winner.name] = winrate.get(winner.name, 0) + 1

    print(winrate)


if __name__ == "__main__":
    main()
