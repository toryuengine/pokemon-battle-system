from ability.shared import ContactStatusAbility


# ほのおのからだ: 接触技を受けると30%の確率で相手をやけどにする
class FlameBody(ContactStatusAbility):
    conditions = ("burn",)

    def __init__(self):
        super().__init__(id=86)
