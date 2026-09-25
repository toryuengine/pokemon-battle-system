from ability.shared import TypeAbsorbAbility


# でんきエンジン: でんき技を受けると、ダメージ・効果を受けずに素早さが1段階上がる
class MotorDrive(TypeAbsorbAbility):
    absorbed_type = "でんき"

    def __init__(self):
        super().__init__(id=85)

    def on_absorb(self, battle, pokemon):
        battle.change_stage(pokemon, "spd", 1)
