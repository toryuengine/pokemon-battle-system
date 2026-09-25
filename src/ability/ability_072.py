from ability.base_ability import BaseAbility
from battlelogic.stat_stage import stage_multiplier


# ダウンロード: 場に出た時、相手の防御が特防より低ければ攻撃を、そうでなければ特攻を1段階上げる
class Download(BaseAbility):
    def __init__(self):
        super().__init__(id=72)

    def on_switch_in(self, battle, pokemon):
        opponent = battle.get_opponent(pokemon)
        if battle.is_fainted(opponent):
            return
        stages = battle.get_stages(opponent)
        defense = opponent.status.defense * stage_multiplier(stages.defense)
        spdef = opponent.status.spdef * stage_multiplier(stages.spdef)
        battle.change_stage(pokemon, "atk" if defense < spdef else "spatk", 1)
