import random

from core.battle import Battle
from pokemon import Pokemon


def main():
    winrate = {}

    for i in range(10000):
        pokemon1 = Pokemon(1, 2)
        pokemon2 = Pokemon(3, 0)
        battle = Battle(pokemon1, pokemon2)

        turn = 0
        while battle.get_winner() is None:
            attacker, defender = (pokemon1, pokemon2) if turn % 2 == 0 else (pokemon2, pokemon1)
            move = random.choice(attacker.moves)
            battle.use_move(attacker, defender, move)
            turn += 1

        winner = battle.get_winner()
        winrate[winner.name] = winrate.get(winner.name, 0) + 1

    print(winrate)


if __name__ == "__main__":
    main()
