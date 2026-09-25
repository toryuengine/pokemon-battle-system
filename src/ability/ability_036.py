from ability.base_ability import BaseAbility


# はやおき: ねむりの残りターンが2倍の速さで減る
class EarlyBird(BaseAbility):
    sleep_turn_decrement = 2

    def __init__(self):
        super().__init__(id=36)
