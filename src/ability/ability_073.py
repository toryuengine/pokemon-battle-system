from ability.base_ability import BaseAbility


# かそく: ターン終了時に素早さが1段階上がる
class SpeedBoost(BaseAbility):
    def __init__(self):
        super().__init__(id=73)

    def on_end_of_turn(self, battle, pokemon):
        # 素早さが既に最大（+6）なら上がらず、メッセージも出ない
        if battle.get_stages(pokemon).spd < 6:
            battle.reveal_ability(pokemon, self)
        battle.change_stage(pokemon, "spd", 1)
