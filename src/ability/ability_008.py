from ability.base_ability import BaseAbility


# しめりけ: 場にいる間、自分・相手のだいばくはつを失敗させる（使った側も瀕死にならない）。かたやぶりの相手には無視される
# 場にいる間、ゆうばくも発動しなくなる（こちらはかたやぶりでも無視できない）
class Damp(BaseAbility):
    is_breakable = True
    prevents_self_destruct = True

    def __init__(self):
        super().__init__(id=8)
