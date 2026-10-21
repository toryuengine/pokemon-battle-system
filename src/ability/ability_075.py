from ability.base_ability import BaseAbility


# ふくつのこころ: ひるむと素早さが1段階上がる
class Steadfast(BaseAbility):
    def __init__(self):
        super().__init__(id=75)

    def on_flinched(self, battle, pokemon):
        if battle.get_stages(pokemon).spd < 6:
            battle.reveal_ability(pokemon, self)
        battle.change_stage(pokemon, "spd", 1)
