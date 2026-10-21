from ability.shared import AnnouncedOnSwitchInAbility


# かたやぶり: 相手の特性（受ける側で働くもの）を無視して技を出す。場に出た時にメッセージが出る
class MoldBreaker(AnnouncedOnSwitchInAbility):
    ignores_target_ability = True

    def __init__(self):
        super().__init__(id=62)
