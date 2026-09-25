from ability.base_ability import BaseAbility


# かそく: ターン終了時に素早さが1段階上がる
class SpeedBoost(BaseAbility):
    def __init__(self):
        super().__init__(id=73)

    def on_end_of_turn(self, battle, pokemon):
        battle.change_stage(pokemon, "spd", 1)
