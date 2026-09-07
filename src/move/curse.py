from move.base_move import BaseMove


# のろい
class Curse(BaseMove):
    def __init__(self):
        super().__init__(id=10)
        self.normal_atk_up_stage = 1
        self.normal_def_up_stage = 1
        self.normal_speed_down_stage = 1
        self.ghost_self_hp_cost_ratio = 0.5
        self.ghost_target_damage_ratio = 0.25
