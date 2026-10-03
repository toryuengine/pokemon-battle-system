from ability.shared import ContactStatusAbility


# どくのトゲ: 接触技を受けると30%の確率で相手をどくにする
class PoisonPoint(ContactStatusAbility):
    conditions = ("poison",)

    def __init__(self):
        super().__init__(id=53)
