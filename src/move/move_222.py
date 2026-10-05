from move.base_move import BaseMove


# つのドリル
class HornDrill(BaseMove):
    def __init__(self):
        super().__init__(id=222)
        self.makes_contact = True
        self.effects = []
        self.is_ohko = True
