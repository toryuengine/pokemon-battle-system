from item.base_item import BaseItem

WIDE_LENS_MULTIPLIER = 1.1
ZOOM_LENS_MULTIPLIER = 1.2
EVASION_ITEM_MULTIPLIER = 0.9


# こうかくレンズ: 命中率1.1倍
class WideLens(BaseItem):
    def get_accuracy_multiplier(self, attacker, defender) -> float:
        return WIDE_LENS_MULTIPLIER


# フォーカスレンズ: 相手がこのターン既に行動していれば命中率1.2倍
class ZoomLens(BaseItem):
    def get_accuracy_multiplier(self, attacker, defender) -> float:
        return ZOOM_LENS_MULTIPLIER if defender.current_status.has_moved_this_turn else 1.0


# ひかりのこな・のんきのおこう: 持ち主に向けられた技の命中率0.9倍
class EvasionItem(BaseItem):
    def get_received_accuracy_multiplier(self) -> float:
        return EVASION_ITEM_MULTIPLIER
