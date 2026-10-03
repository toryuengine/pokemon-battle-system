from ability.shared import ContactStatusAbility


# ほうし: 接触技を受けると30%の確率で相手をどく・まひ・ねむりのどれか（1/3ずつ）にする
class EffectSpore(ContactStatusAbility):
    conditions = ("poison", "paralysis", "sleep")

    def __init__(self):
        super().__init__(id=18)
