from move.base_move import BaseMove


# かみくだく
class Crunch(BaseMove):
    def __init__(self):
        super().__init__(id=23)
        self.defense_down_chance = 0.2
        self.defense_down_stage = 1

    def apply_effect(self, battle, attacker, defender):
        battle.try_apply_stat_change(defender, "defense", -self.defense_down_stage, self.defense_down_chance)
