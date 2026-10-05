from move.base_move import BaseMove


# かみなりのキバ
class ThunderFang(BaseMove):
    def __init__(self):
        super().__init__(id=82)
        self.makes_contact = True
        self.effects = [('status', 'target', 'paralysis', 0.1), ('flinch', 'target', 0.1)]
