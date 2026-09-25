from ability.base_ability import BaseAbility

# シンクロで相手にうつす状態異常（ねむり・こおりはうつさない）
SYNCHRONIZED_CONDITIONS = {"poison", "paralysis", "burn"}


# シンクロ: 相手にどく・まひ・やけどにされると、相手も同じ状態異常にする
class Synchronize(BaseAbility):
    def __init__(self):
        super().__init__(id=49)

    def on_status_inflicted(self, battle, pokemon, condition, source):
        if source is None or source is pokemon or condition not in SYNCHRONIZED_CONDITIONS:
            return
        battle.try_apply_status(source, condition, 1.0)
