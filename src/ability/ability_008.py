from ability.base_ability import BaseAbility


# しめりけ: 場にいる間、自分・相手のだいばくはつを失敗させる（使った側も瀕死にならない）。かたやぶりの相手には無視される
# ゆうばくを不発にする効果は、技の接触判定が無くゆうばく自体が未実装のため未実装
class Damp(BaseAbility):
    is_breakable = True
    prevents_self_destruct = True

    def __init__(self):
        super().__init__(id=8)
